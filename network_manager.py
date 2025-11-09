#!/usr/bin/env python3
"""
Network Manager
Handles WiFi connectivity detection and manages offline/online operations
"""

import os
import json
import subprocess
import time
from datetime import datetime
from typing import Optional, Dict, List
import logging
from collections import deque


class NetworkManager:
    """Manages network connectivity and offline operation queues"""
    
    def __init__(self, queue_dir="data/queue"):
        self.queue_dir = queue_dir
        self.logger = self._setup_logger()
        self.is_online = False
        self.queue = deque()
        
        # Ensure queue directory exists
        os.makedirs(self.queue_dir, exist_ok=True)
        
        # Load pending queue from disk
        self._load_queue()
    
    def _setup_logger(self):
        """Setup logging"""
        logger = logging.getLogger('NetworkManager')
        logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        fh = logging.FileHandler('logs/network_manager.log')
        fh.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def check_connectivity(self) -> bool:
        """
        Check if internet/WiFi is available
        
        Returns:
            True if connected, False otherwise
        """
        try:
            # Try to ping Google DNS
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', '8.8.8.8'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3
            )
            
            was_online = self.is_online
            self.is_online = (result.returncode == 0)
            
            # Log status change
            if was_online != self.is_online:
                if self.is_online:
                    self.logger.info("✓ WiFi/Internet connection established")
                else:
                    self.logger.warning("✗ WiFi/Internet connection lost - switching to offline mode")
            
            return self.is_online
            
        except Exception as e:
            self.logger.debug(f"Connectivity check failed: {e}")
            self.is_online = False
            return False
    
    def queue_operation(self, operation_type: str, data: Dict, priority: int = 0):
        """
        Queue an operation that requires internet connectivity
        
        Args:
            operation_type: Type of operation (e.g., 'google_maps_lookup', 'reverse_geocode')
            data: Operation data
            priority: Priority level (higher = more important)
        """
        operation = {
            'id': f"{operation_type}_{datetime.now().timestamp()}",
            'type': operation_type,
            'data': data,
            'priority': priority,
            'timestamp': datetime.now().isoformat(),
            'attempts': 0,
            'status': 'queued'
        }
        
        self.queue.append(operation)
        self._save_queue()
        
        self.logger.info(f"Queued operation: {operation_type} (queue size: {len(self.queue)})")
    
    def _save_queue(self):
        """Save queue to disk for persistence"""
        queue_file = os.path.join(self.queue_dir, 'pending_operations.json')
        
        with open(queue_file, 'w') as f:
            json.dump(list(self.queue), f, indent=2)
    
    def _load_queue(self):
        """Load queue from disk"""
        queue_file = os.path.join(self.queue_dir, 'pending_operations.json')
        
        if os.path.exists(queue_file):
            try:
                with open(queue_file, 'r') as f:
                    operations = json.load(f)
                    self.queue = deque(operations)
                    self.logger.info(f"Loaded {len(self.queue)} pending operations from disk")
            except Exception as e:
                self.logger.error(f"Failed to load queue: {e}")
                self.queue = deque()
    
    def get_queued_operations(self, operation_type: Optional[str] = None) -> List[Dict]:
        """
        Get queued operations, optionally filtered by type
        
        Args:
            operation_type: Optional filter by operation type
        
        Returns:
            List of queued operations
        """
        if operation_type:
            return [op for op in self.queue if op['type'] == operation_type]
        return list(self.queue)
    
    def mark_operation_complete(self, operation_id: str):
        """
        Mark an operation as complete and remove from queue
        
        Args:
            operation_id: ID of the operation
        """
        self.queue = deque([op for op in self.queue if op['id'] != operation_id])
        self._save_queue()
    
    def mark_operation_failed(self, operation_id: str, error: str):
        """
        Mark an operation as failed
        
        Args:
            operation_id: ID of the operation
            error: Error message
        """
        for op in self.queue:
            if op['id'] == operation_id:
                op['attempts'] += 1
                op['last_error'] = error
                op['last_attempt'] = datetime.now().isoformat()
                
                # Remove if too many attempts
                if op['attempts'] >= 3:
                    self.logger.warning(f"Operation {operation_id} failed after 3 attempts, removing")
                    self.queue.remove(op)
                
                break
        
        self._save_queue()
    
    def get_queue_size(self) -> int:
        """Get number of queued operations"""
        return len(self.queue)
    
    def clear_queue(self):
        """Clear all queued operations"""
        self.queue.clear()
        self._save_queue()
        self.logger.info("Queue cleared")
    
    def get_network_status(self) -> Dict:
        """
        Get detailed network status
        
        Returns:
            Network status information
        """
        return {
            'is_online': self.is_online,
            'queue_size': len(self.queue),
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Test network manager"""
    manager = NetworkManager()
    
    print("Testing network connectivity...")
    for i in range(5):
        status = manager.check_connectivity()
        print(f"Attempt {i+1}: {'Online' if status else 'Offline'}")
        time.sleep(2)
    
    # Test queuing
    if not manager.is_online:
        manager.queue_operation('test_operation', {'data': 'test'})
        print(f"Queue size: {manager.get_queue_size()}")


if __name__ == '__main__':
    main()
