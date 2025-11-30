"""
Embedding Generator using AWS Bedrock Titan Embeddings V2

Generates embeddings for text chunks to enable semantic search in OpenSearch.
"""

import boto3
import json
from typing import List
import time


class EmbeddingGenerator:
    """Generate embeddings using AWS Bedrock Titan Embeddings V2.

    Attributes:
        bedrock (boto3.client): The AWS Bedrock runtime client.
        model_id (str): The ID of the model to use for embeddings.
    """

    def __init__(self, region_name: str = 'us-east-1'):
        """Initialize Bedrock client.

        Args:
            region_name (str): AWS region name. Defaults to 'us-east-1'.
        """
        self.bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name
        )
        self.model_id = 'amazon.titan-embed-text-v2:0'

    def embed_text(self, text: str, input_type: str = 'search_document') -> List[float]:
        """Generate embedding for a single text string.

        Args:
            text (str): Text to embed (max ~8000 tokens).
            input_type (str): 'search_document' for indexing, 'search_query' for queries.
                Defaults to 'search_document'.

        Returns:
            List[float]: List of floats representing the embedding vector (1024 dimensions).

        Raises:
            Exception: If there is an error invoking the Bedrock model.
        """
        # Truncate if too long (Titan v2 max is ~8000 tokens, roughly 30k chars)
        if len(text) > 30000:
            text = text[:30000]

        request_body = {
            "inputText": text,
            "dimensions": 1024,
            "normalize": True
        }

        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )

            response_body = json.loads(response['body'].read())
            return response_body['embedding']

        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def embed_batch(self, texts: List[str], input_type: str = 'search_document',
                   batch_size: int = 10, delay: float = 0.1) -> List[List[float]]:
        """Generate embeddings for multiple texts with rate limiting.

        Args:
            texts (List[str]): List of texts to embed.
            input_type (str): 'search_document' for indexing, 'search_query' for queries.
                Defaults to 'search_document'.
            batch_size (int): Process this many at once before delay. Defaults to 10.
            delay (float): Seconds to wait between batches. Defaults to 0.1.

        Returns:
            List[List[float]]: List of embedding vectors.
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            for text in batch:
                embedding = self.embed_text(text, input_type)
                embeddings.append(embedding)

            # Rate limiting
            if i + batch_size < len(texts):
                time.sleep(delay)

            if (i + batch_size) % 100 == 0:
                print(f"Processed {i + batch_size}/{len(texts)} embeddings")

        return embeddings
