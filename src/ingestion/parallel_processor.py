# src/ingestion/parallel_processor.py
def process_single_paper_lambda(event, context):
    """AWS Lambda handler for processing one paper"""
    pmc_id = event['pmc_id']
    
    # Download XML from PMC
    xml = download_from_pmc(pmc_id)
    
    # Parse
    parser = JATSParser(xml)
    paper = parser.parse()
    
    # Process (with caching)
    pipeline = PaperIndexingPipeline()
    processed = pipeline.process_paper(paper)
    
    # Write to S3 (not OpenSearch yet)
    writer = S3PaperWriter()
    writer.write_paper(processed)
    
    return {'status': 'success', 'pmc_id': pmc_id}
