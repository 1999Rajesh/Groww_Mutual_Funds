"""
Performance Benchmarks for RAG Pipeline
Tests performance metrics for all phases
"""
import time
import numpy as np
from typing import Dict, Any


def benchmark_query_processor() -> Dict[str, float]:
    """Benchmark Phase 5 Query Processor"""
    try:
        from src.rag.query_processor import QueryProcessor
        
        processor = QueryProcessor()
        test_queries = [
            "What is the expense ratio of HDFC ELSS Fund?",
            "Minimum SIP for large cap fund?",
            "Should I invest in HDFC Small Cap?"
        ]
        
        # Warm-up
        for query in test_queries:
            processor.process_query(query)
        
        # Benchmark
        start = time.perf_counter()
        for _ in range(100):
            for query in test_queries:
                processor.process_query(query)
        end = time.perf_counter()
        
        total_time = end - start
        avg_time_per_query = (total_time / (len(test_queries) * 100)) * 1000  # ms
        
        return {
            'query_processor_total_ms': round(total_time * 1000, 2),
            'query_processor_avg_per_query_ms': round(avg_time_per_query, 3),
            'queries_processed': len(test_queries) * 100
        }
    
    except Exception as e:
        return {'error': str(e)}


def benchmark_embedding_generation() -> Dict[str, float]:
    """Benchmark Phase 3 Embedding Generation"""
    try:
        from src.embeddings.embedding_generator import EmbeddingGenerator
        
        generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
        test_texts = [
            "HDFC ELSS Tax Saver Fund has an expense ratio of 0.68%",
            "Minimum SIP amount is ₹500",
            "Lock-in period is 3 years"
        ]
        
        # Warm-up
        generator.generate_embeddings(test_texts, show_progress=False)
        
        # Benchmark
        num_batches = 10
        start = time.perf_counter()
        for _ in range(num_batches):
            generator.generate_embeddings(test_texts, show_progress=False)
        end = time.perf_counter()
        
        total_time = end - start
        avg_time_per_batch = total_time / num_batches
        
        return {
            'embedding_total_time_ms': round(total_time * 1000, 2),
            'embedding_avg_per_batch_ms': round(avg_time_per_batch * 1000, 2),
            'batches_processed': num_batches,
            'embeddings_per_batch': len(test_texts)
        }
    
    except Exception as e:
        return {'error': str(e)}


def run_benchmarks() -> Dict[str, Any]:
    """Run all performance benchmarks"""
    print("\nRunning Performance Benchmarks...")
    print("="*80)
    
    results = {}
    
    # Benchmark each component
    print("\n1. Query Processor Benchmark")
    print("-"*80)
    qp_results = benchmark_query_processor()
    results.update(qp_results)
    print(f"Query Processor Results: {qp_results}")
    
    print("\n2. Embedding Generator Benchmark")
    print("-"*80)
    emb_results = benchmark_embedding_generation()
    results.update(emb_results)
    print(f"Embedding Generator Results: {emb_results}")
    
    print("\n" + "="*80)
    print("BENCHMARK SUMMARY")
    print("="*80)
    
    for metric, value in results.items():
        if not metric.startswith('error'):
            print(f"{metric}: {value}")
    
    return results


if __name__ == "__main__":
    results = run_benchmarks()
    print("\n✅ Benchmarks complete!")
