"""
Time Synchronization Utility for Binance API
"""
import time
import requests
import sys


def check_time_sync(testnet: bool = True) -> dict:
    """
    Check time synchronization with Binance server
    
    Args:
        testnet: Whether to check testnet or mainnet
    
    Returns:
        Dictionary with sync status and time difference
    """
    try:
        if testnet:
            base_url = 'https://testnet.binancefuture.com'
        else:
            base_url = 'https://fapi.binance.com'
        
        # Get server time
        response = requests.get(f'{base_url}/fapi/v1/time', timeout=5)
        server_time = response.json()['serverTime']
        
        # Get local time
        local_time = int(time.time() * 1000)
        
        # Calculate difference
        time_diff = server_time - local_time
        
        return {
            'synced': abs(time_diff) < 1000,  # Within 1 second
            'time_diff_ms': time_diff,
            'server_time': server_time,
            'local_time': local_time,
            'status': 'OK' if abs(time_diff) < 1000 else 'OUT_OF_SYNC'
        }
    except Exception as e:
        return {
            'synced': False,
            'error': str(e),
            'status': 'ERROR'
        }


def print_time_sync_info():
    """Print time synchronization information"""
    print("Checking time synchronization with Binance Testnet...")
    result = check_time_sync(testnet=True)
    
    if result.get('status') == 'OK':
        print(f"[OK] Time is synchronized (difference: {result['time_diff_ms']}ms)")
    elif result.get('status') == 'OUT_OF_SYNC':
        print(f"[WARNING] Time is out of sync (difference: {result['time_diff_ms']}ms)")
        print("\nTo fix this:")
        print("1. Windows: Run 'w32tm /resync' as administrator")
        print("2. Or sync your system clock with internet time in Windows Settings")
        print("3. Make sure your timezone is correct")
    else:
        print(f"[ERROR] Error checking time sync: {result.get('error', 'Unknown error')}")
    
    return result


if __name__ == '__main__':
    print_time_sync_info()
