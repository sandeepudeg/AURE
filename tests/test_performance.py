"""
Performance and Scalability Testing for URE MVP
Tests with 50-100 concurrent users and 1000+ users
"""

import pytest
import time
import statistics
import concurrent.futures
import requests
import json
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

# API Gateway URL from environment
API_GATEWAY_URL = os.getenv('API_GATEWAY_URL', 'http://localhost:8000/query')


class TestPerformance:
    """Performance tests with 50-100 concurrent users"""
    
    def simulate_user_request(self, user_id: int, query: str) -> Dict:
        """Simulate a single user request"""
        start_time = time.time()
        
        try:
            response = requests.post(
                API_GATEWAY_URL,
                json={
                    'user_id': f'test_user_{user_id}',
                    'query': query,
                    'language': 'en'
                },
                timeout=10
            )
            
            elapsed_time = time.time() - start_time
            
            return {
                'user_id': user_id,
                'status_code': response.status_code,
                'elapsed_time': elapsed_time,
                'success': response.status_code == 200,
                'error': None
            }
        
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                'user_id': user_id,
                'status_code': 0,
                'elapsed_time': elapsed_time,
                'success': False,
                'error': str(e)
            }
    
    def test_response_time_single_user(self):
        """Test response time for single user (baseline)"""
        query = "What are the symptoms of tomato late blight?"
        
        result = self.simulate_user_request(1, query)
        
        # Response time should be < 5 seconds
        assert result['elapsed_time'] < 5.0, f"Response time {result['elapsed_time']}s exceeds 5s SLA"
        
        print(f"\nSingle user response time: {result['elapsed_time']:.2f}s")
    
    def test_concurrent_50_users(self):
        """Test with 50 concurrent users"""
        num_users = 50
        queries = [
            "What disease is affecting my tomato plant?",
            "How do I apply for PM-Kisan scheme?",
            "When should I irrigate my wheat field?",
            "What are the market prices for onions?",
            "What is the weather forecast for next week?"
        ]
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for i in range(num_users):
                query = queries[i % len(queries)]
                future = executor.submit(self.simulate_user_request, i, query)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        # Analyze results
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        response_times = [r['elapsed_time'] for r in successful_requests]
        
        # Calculate statistics
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            max_time = max(response_times)
            
            success_rate = len(successful_requests) / num_users * 100
            
            print(f"\n50 Concurrent Users Test Results:")
            print(f"  Total requests: {num_users}")
            print(f"  Successful: {len(successful_requests)} ({success_rate:.1f}%)")
            print(f"  Failed: {len(failed_requests)}")
            print(f"  Avg response time: {avg_time:.2f}s")
            print(f"  Median response time: {median_time:.2f}s")
            print(f"  95th percentile: {p95_time:.2f}s")
            print(f"  Max response time: {max_time:.2f}s")
            
            # Assertions
            assert success_rate >= 95, f"Success rate {success_rate}% is below 95%"
            assert p95_time < 5.0, f"95th percentile {p95_time}s exceeds 5s SLA"
        else:
            pytest.fail("No successful requests in 50 concurrent users test")
    
    def test_concurrent_100_users(self):
        """Test with 100 concurrent users"""
        num_users = 100
        queries = [
            "What disease is affecting my tomato plant?",
            "How do I apply for PM-Kisan scheme?",
            "When should I irrigate my wheat field?",
            "What are the market prices for onions?",
            "What is the weather forecast for next week?"
        ]
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            for i in range(num_users):
                query = queries[i % len(queries)]
                future = executor.submit(self.simulate_user_request, i, query)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        # Analyze results
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        response_times = [r['elapsed_time'] for r in successful_requests]
        
        # Calculate statistics
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            max_time = max(response_times)
            
            success_rate = len(successful_requests) / num_users * 100
            
            print(f"\n100 Concurrent Users Test Results:")
            print(f"  Total requests: {num_users}")
            print(f"  Successful: {len(successful_requests)} ({success_rate:.1f}%)")
            print(f"  Failed: {len(failed_requests)}")
            print(f"  Avg response time: {avg_time:.2f}s")
            print(f"  Median response time: {median_time:.2f}s")
            print(f"  95th percentile: {p95_time:.2f}s")
            print(f"  Max response time: {max_time:.2f}s")
            
            # Assertions (slightly relaxed for 100 users)
            assert success_rate >= 90, f"Success rate {success_rate}% is below 90%"
            assert p95_time < 7.0, f"95th percentile {p95_time}s exceeds 7s"
        else:
            pytest.fail("No successful requests in 100 concurrent users test")
    
    def test_throughput(self):
        """Test system throughput (requests per second)"""
        num_requests = 100
        query = "What are the symptoms of tomato late blight?"
        
        start_time = time.time()
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(self.simulate_user_request, i, query)
                for i in range(num_requests)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        total_time = time.time() - start_time
        successful_requests = len([r for r in results if r['success']])
        
        throughput = successful_requests / total_time
        
        print(f"\nThroughput Test Results:")
        print(f"  Total requests: {num_requests}")
        print(f"  Successful: {successful_requests}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Throughput: {throughput:.2f} requests/second")
        
        # Throughput should be ≥ 10 requests/second
        assert throughput >= 10, f"Throughput {throughput:.2f} req/s is below 10 req/s target"


class TestScalability:
    """Scalability tests with 1000+ users"""
    
    def simulate_user_request(self, user_id: int, query: str) -> Dict:
        """Simulate a single user request"""
        start_time = time.time()
        
        try:
            response = requests.post(
                API_GATEWAY_URL,
                json={
                    'user_id': f'test_user_{user_id}',
                    'query': query,
                    'language': 'en'
                },
                timeout=15
            )
            
            elapsed_time = time.time() - start_time
            
            return {
                'user_id': user_id,
                'status_code': response.status_code,
                'elapsed_time': elapsed_time,
                'success': response.status_code == 200,
                'error': None
            }
        
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                'user_id': user_id,
                'status_code': 0,
                'elapsed_time': elapsed_time,
                'success': False,
                'error': str(e)
            }
    
    @pytest.mark.slow
    def test_concurrent_500_users(self):
        """Test with 500 concurrent users"""
        num_users = 500
        queries = [
            "What disease is affecting my tomato plant?",
            "How do I apply for PM-Kisan scheme?",
            "When should I irrigate my wheat field?",
            "What are the market prices for onions?",
            "What is the weather forecast for next week?"
        ]
        
        results = []
        
        print(f"\nStarting 500 concurrent users test...")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            for i in range(num_users):
                query = queries[i % len(queries)]
                future = executor.submit(self.simulate_user_request, i, query)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        response_times = [r['elapsed_time'] for r in successful_requests]
        
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            p95_time = statistics.quantiles(response_times, n=20)[18]
            
            success_rate = len(successful_requests) / num_users * 100
            
            print(f"\n500 Concurrent Users Test Results:")
            print(f"  Total requests: {num_users}")
            print(f"  Successful: {len(successful_requests)} ({success_rate:.1f}%)")
            print(f"  Failed: {len(failed_requests)}")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Avg response time: {avg_time:.2f}s")
            print(f"  Median response time: {median_time:.2f}s")
            print(f"  95th percentile: {p95_time:.2f}s")
            
            # Assertions (relaxed for high load)
            assert success_rate >= 85, f"Success rate {success_rate}% is below 85%"
            assert p95_time < 10.0, f"95th percentile {p95_time}s exceeds 10s"
    
    @pytest.mark.slow
    def test_concurrent_1000_users(self):
        """Test with 1000 concurrent users"""
        num_users = 1000
        queries = [
            "What disease is affecting my tomato plant?",
            "How do I apply for PM-Kisan scheme?",
            "When should I irrigate my wheat field?",
            "What are the market prices for onions?",
            "What is the weather forecast for next week?"
        ]
        
        results = []
        
        print(f"\nStarting 1000 concurrent users test...")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            for i in range(num_users):
                query = queries[i % len(queries)]
                future = executor.submit(self.simulate_user_request, i, query)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        response_times = [r['elapsed_time'] for r in successful_requests]
        
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            p95_time = statistics.quantiles(response_times, n=20)[18]
            
            success_rate = len(successful_requests) / num_users * 100
            
            print(f"\n1000 Concurrent Users Test Results:")
            print(f"  Total requests: {num_users}")
            print(f"  Successful: {len(successful_requests)} ({success_rate:.1f}%)")
            print(f"  Failed: {len(failed_requests)}")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Avg response time: {avg_time:.2f}s")
            print(f"  Median response time: {median_time:.2f}s")
            print(f"  95th percentile: {p95_time:.2f}s")
            
            # Assertions (relaxed for very high load)
            assert success_rate >= 80, f"Success rate {success_rate}% is below 80%"
            assert p95_time < 15.0, f"95th percentile {p95_time}s exceeds 15s"
    
    def test_auto_scaling(self):
        """Test that system can handle gradual load increase"""
        load_levels = [10, 50, 100, 200]
        query = "What are the symptoms of tomato late blight?"
        
        results_by_load = {}
        
        for num_users in load_levels:
            print(f"\nTesting with {num_users} users...")
            
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = [
                    executor.submit(self.simulate_user_request, i, query)
                    for i in range(num_users)
                ]
                
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())
            
            successful = [r for r in results if r['success']]
            response_times = [r['elapsed_time'] for r in successful]
            
            if response_times:
                avg_time = statistics.mean(response_times)
                success_rate = len(successful) / num_users * 100
                
                results_by_load[num_users] = {
                    'avg_time': avg_time,
                    'success_rate': success_rate
                }
                
                print(f"  Avg time: {avg_time:.2f}s, Success rate: {success_rate:.1f}%")
        
        # Verify no significant degradation
        for num_users, metrics in results_by_load.items():
            assert metrics['success_rate'] >= 85, \
                f"Success rate {metrics['success_rate']}% at {num_users} users is below 85%"


if __name__ == "__main__":
    # Run performance tests (exclude slow scalability tests by default)
    pytest.main([__file__, '-v', '-m', 'not slow', '--tb=short'])
