import random
import string
import json
import logging
import requests
from typing import Dict, List, Union, Optional, Any
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FuzzingStrategy(BaseModel):
    """Base model for fuzzing strategies"""
    name: str
    description: str
    
    def generate(self) -> Any:
        raise NotImplementedError

class StringFuzzer(FuzzingStrategy):
    """Generates fuzzed string data"""
    name: str = "StringFuzzer"
    description: str = "Generates random or malformed strings"
    min_length: int = 1
    max_length: int = 1000
    include_special: bool = True
    include_sql_injection: bool = True
    include_xss: bool = True
    
    def generate(self) -> str:
        strategy = random.choice([
            self._random_string,
            self._sql_injection if self.include_sql_injection else self._random_string,
            self._xss_payload if self.include_xss else self._random_string,
            self._long_string,
            self._unicode_string
        ])
        return strategy()
    
    def _random_string(self) -> str:
        length = random.randint(self.min_length, min(100, self.max_length))
        chars = string.ascii_letters + string.digits
        if self.include_special:
            chars += string.punctuation
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _sql_injection(self) -> str:
        payloads = [
            "' OR 1=1; --",
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT username, password FROM users; --"
        ]
        return random.choice(payloads)
    
    def _xss_payload(self) -> str:
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src='x' onerror='alert(1)'>",
            "javascript:alert(document.cookie)",
            "onmouseover='alert(1)'",
            "' onload='alert(1)"
        ]
        return random.choice(payloads)
    
    def _long_string(self) -> str:
        return 'A' * random.randint(100, self.max_length)
    
    def _unicode_string(self) -> str:
        unicode_chars = [chr(i) for i in range(0x1000, 0x3000)]
        length = random.randint(self.min_length, min(100, self.max_length))
        return ''.join(random.choice(unicode_chars) for _ in range(length))

class NumberFuzzer(FuzzingStrategy):
    """Generates fuzzed numeric data"""
    name: str = "NumberFuzzer"
    description: str = "Generates boundary and special case numbers"
    
    def generate(self) -> Union[int, float]:
        strategy = random.choice([
            self._boundary_int,
            self._special_float,
            self._negative_number,
            self._large_number
        ])
        return strategy()
    
    def _boundary_int(self) -> int:
        boundaries = [0, 1, -1, 255, 256, 65535, 65536, 2147483647, 2147483648, -2147483648]
        return random.choice(boundaries)
    
    def _special_float(self) -> float:
        specials = [0.0, -0.0, float('inf'), float('-inf'), float('nan')]
        return random.choice(specials)
    
    def _negative_number(self) -> int:
        return -random.randint(1, 1000000)
    
    def _large_number(self) -> int:
        return random.randint(1000000, 1000000000)

class StructureFuzzer(FuzzingStrategy):
    """Fuzzes data structures like JSON"""
    name: str = "StructureFuzzer" 
    description: str = "Creates malformed or unusual data structures"
    
    def generate(self) -> Dict:
        strategy = random.choice([
            self._deeply_nested,
            self._missing_fields,
            self._extra_fields,
            self._mixed_types
        ])
        return strategy()
    
    def _deeply_nested(self, depth=0) -> Dict:
        if depth > 10:
            return {"value": "leaf"}
        
        return {
            "nested": self._deeply_nested(depth + 1)
        }
    
    def _missing_fields(self) -> Dict:
        templates = [
            {"user": {"name": "test", "id": 123}},
            {"query": {"filter": "status=active"}},
            {"config": {"timeout": 30, "retries": 3}}
        ]
        
        template = random.choice(templates)
        # Remove random key
        if template:
            main_key = random.choice(list(template.keys()))
            if template[main_key]:
                to_remove = random.choice(list(template[main_key].keys()))
                template[main_key].pop(to_remove)
        
        return template
    
    def _extra_fields(self) -> Dict:
        base = {"id": 123, "name": "test"}
        extra_count = random.randint(1, 10)
        
        for _ in range(extra_count):
            key = f"extra_{random.randint(1, 1000)}"
            base[key] = random.choice([
                "extra_value",
                random.randint(1, 1000),
                True,
                None,
                ["item1", "item2"]
            ])
        
        return base
    
    def _mixed_types(self) -> Dict:
        return {
            "string_or_int": random.choice(["string", 123]),
            "array_or_object": random.choice([
                ["item1", "item2"],
                {"key1": "value1", "key2": "value2"}
            ]),
            "null_or_value": random.choice([None, "value", 42]),
            "nested": {
                "mixed": random.choice([[], {}, "", 0])
            }
        }

class ApiFuzzer:
    """Main API fuzzing class"""
    
    def __init__(self, base_url: str, endpoints: List[str], 
                auth_headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.endpoints = endpoints
        self.auth_headers = auth_headers or {}
        
        self.fuzzers = {
            "string": StringFuzzer(),
            "number": NumberFuzzer(),
            "structure": StructureFuzzer()
        }
        
        self.results = {
            "total_tests": 0,
            "failures": 0,
            "success": 0,
            "issues": []
        }
    
    def get_fuzzer(self, fuzzer_type: str) -> FuzzingStrategy:
        """Get a specific fuzzer by type"""
        return self.fuzzers.get(fuzzer_type, self.fuzzers["string"])
    
    def fuzz_parameter(self, endpoint: str, param_name: str, 
                      method: str = "GET", rounds: int = 10,
                      fuzzer_type: str = "string") -> Dict:
        """Fuzz a specific parameter for an endpoint"""
        logger.info(f"Fuzzing parameter '{param_name}' on {endpoint} with {fuzzer_type} fuzzer")
        
        fuzzer = self.get_fuzzer(fuzzer_type)
        results = {
            "endpoint": endpoint,
            "parameter": param_name,
            "method": method,
            "tests": rounds,
            "issues": []
        }
        
        for i in range(rounds):
            fuzz_value = fuzzer.generate()
            url = f"{self.base_url}/{endpoint}"
            
            try:
                if method.upper() == "GET":
                    params = {param_name: fuzz_value}
                    response = requests.get(
                        url, 
                        params=params, 
                        headers=self.auth_headers,
                        timeout=10
                    )
                else:  # POST
                    data = {param_name: fuzz_value}
                    response = requests.post(
                        url, 
                        json=data, 
                        headers=self.auth_headers,
                        timeout=10
                    )
                
                self.results["total_tests"] += 1
                
                # Check for interesting responses
                if response.status_code >= 500:
                    issue = {
                        "value": str(fuzz_value)[:100],
                        "status_code": response.status_code,
                        "response": response.text[:200]
                    }
                    results["issues"].append(issue)
                    self.results["issues"].append({
                        "endpoint": endpoint,
                        "parameter": param_name,
                        "value": str(fuzz_value)[:100],
                        "status_code": response.status_code
                    })
                    self.results["failures"] += 1
                    logger.warning(f"Found issue: {issue}")
                else:
                    self.results["success"] += 1
                    
            except Exception as e:
                self.results["total_tests"] += 1
                self.results["failures"] += 1
                
                issue = {
                    "value": str(fuzz_value)[:100],
                    "exception": str(e)
                }
                results["issues"].append(issue)
                self.results["issues"].append({
                    "endpoint": endpoint,
                    "parameter": param_name,
                    "value": str(fuzz_value)[:100],
                    "exception": str(e)
                })
                logger.warning(f"Exception when fuzzing {endpoint}: {e}")
        
        return results
    
    def fuzz_all_endpoints(self, 
                         default_params: Dict[str, str] = None,
                         rounds_per_endpoint: int = 5) -> Dict:
        """Fuzz all configured endpoints"""
        default_params = default_params or {"q": "string", "id": "number"}
        
        logger.info(f"Starting fuzzing of {len(self.endpoints)} endpoints")
        
        for endpoint in self.endpoints:
            for param_name, fuzzer_type in default_params.items():
                self.fuzz_parameter(
                    endpoint=endpoint,
                    param_name=param_name,
                    fuzzer_type=fuzzer_type,
                    rounds=rounds_per_endpoint
                )
        
        return self.results
    
    def export_results(self, filename: str) -> None:
        """Export fuzzing results to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Exported results to {filename}")
