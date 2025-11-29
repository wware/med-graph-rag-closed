"""
Test Queries Script

Interactive tool for testing queries against the medical knowledge graph.
Supports semantic search, keyword search, and hybrid search.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.client.medical_papers_client import MedicalPapersClient


def interactive_mode(client: MedicalPapersClient):
    """Interactive query testing mode"""
    print("=== Medical Knowledge Graph - Interactive Query Mode ===")
    print("Enter your queries below. Type 'quit' or 'exit' to exit.")
    print("Commands:")
    print("  semantic <query>  - Semantic search using embeddings")
    print("  keyword <query>   - Keyword search")
    print("  hybrid <query>    - Hybrid search (semantic + keyword)")
    print("  quit/exit         - Exit interactive mode")
    print()

    while True:
        try:
            query_input = input("Query> ").strip()

            if not query_input:
                continue

            if query_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break

            # Parse command
            parts = query_input.split(maxsplit=1)
            if len(parts) < 2:
                print("Please specify a search type and query")
                continue

            search_type, query = parts

            # Execute search
            if search_type == 'semantic':
                results = client.semantic_search(query, k=10)
                print(f"\n=== Semantic Search Results for: '{query}' ===")
            elif search_type == 'keyword':
                results = client.keyword_search(query, size=10)
                print(f"\n=== Keyword Search Results for: '{query}' ===")
            elif search_type == 'hybrid':
                results = client.hybrid_search(query)
                print(f"\n=== Hybrid Search Results for: '{query}' ===")
            else:
                print(f"Unknown search type: {search_type}")
                continue

            # Display results
            if not results:
                print("No results found.")
            else:
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result.get('title', 'Unknown Title')} (Score: {result.get('score', 0):.3f})")
                    print(f"   PMC ID: {result.get('pmc_id', 'N/A')}")
                    print(f"   Section: {result.get('section', 'N/A')}")
                    chunk_text = result.get('chunk_text', '')
                    print(f"   {chunk_text[:200]}...")

            print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def run_query(client: MedicalPapersClient, query: str, search_type: str = 'hybrid', k: int = 10):
    """Run a single query and display results"""
    print(f"Running {search_type} search for: '{query}'")

    if search_type == 'semantic':
        results = client.semantic_search(query, k=k)
    elif search_type == 'keyword':
        results = client.keyword_search(query, size=k)
    elif search_type == 'hybrid':
        results = client.hybrid_search(query, k=k)
    else:
        print(f"Unknown search type: {search_type}")
        return

    print(f"\nFound {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. {result.get('title', 'Unknown Title')} (Score: {result.get('score', 0):.3f})")
        print(f"   PMC ID: {result.get('pmc_id', 'N/A')}")
        print(f"   Section: {result.get('section', 'N/A')}")
        chunk_text = result.get('chunk_text', '')
        print(f"   {chunk_text[:200]}...")
        print()


def main():
    parser = argparse.ArgumentParser(description='Test queries against medical knowledge graph')
    parser.add_argument('--opensearch-host', default='localhost',
                       help='OpenSearch host (default: localhost)')
    parser.add_argument('--opensearch-port', type=int, default=9200,
                       help='OpenSearch port (default: 9200)')
    parser.add_argument('--query', type=str,
                       help='Query to run (if not interactive)')
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--search-type', choices=['semantic', 'keyword', 'hybrid'],
                       default='hybrid', help='Type of search to perform')
    parser.add_argument('--k', type=int, default=10,
                       help='Number of results to return (default: 10)')

    args = parser.parse_args()

    # Initialize client
    try:
        client = MedicalPapersClient(
            opensearch_host=args.opensearch_host,
            opensearch_port=args.opensearch_port
        )
        print(f"Connected to OpenSearch at {args.opensearch_host}:{args.opensearch_port}")
    except Exception as e:
        print(f"Error connecting to OpenSearch: {e}")
        sys.exit(1)

    # Run interactive or single query mode
    if args.interactive:
        interactive_mode(client)
    elif args.query:
        run_query(client, args.query, args.search_type, args.k)
    else:
        print("Please specify either --interactive or --query")
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
