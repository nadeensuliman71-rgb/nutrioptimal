"""
Test script to verify that all price scrapers are working correctly
Run this script to test individual scrapers before using the main application
"""

from pricing.scrapers import (
    get_prices_shufersal,
    get_prices_victory,
    get_prices_from_rami_levy
)


def test_shufersal():
    """Test Shufersal scraper"""
    print("=" * 60)
    print("Testing Shufersal Scraper...")
    print("=" * 60)
    
    test_products = ["ביצים", "חלב עוף"]
    
    try:
        prices = get_prices_shufersal(test_products)
        
        print(f"\nResults for Shufersal:")
        for i, (product, price) in enumerate(zip(test_products, prices)):
            print(f"  {product}: {price} NIS per gram")
        
        success = all(p > 0 for p in prices)
        print(f"\nStatus: {'✓ SUCCESS' if success else '✗ FAILED (some prices are 0)'}")
        return success
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_victory():
    """Test Victory scraper"""
    print("\n" + "=" * 60)
    print("Testing Victory Scraper...")
    print("=" * 60)
    
    test_products = ["ביצים", "חלב עוף"]
    
    try:
        prices = get_prices_victory(test_products)
        
        print(f"\nResults for Victory:")
        for i, (product, price) in enumerate(zip(test_products, prices)):
            print(f"  {product}: {price} NIS per gram")
        
        success = all(p > 0 for p in prices)
        print(f"\nStatus: {'✓ SUCCESS' if success else '✗ FAILED (some prices are 0)'}")
        return success
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_rami_levy():
    """Test Rami Levy scraper"""
    print("\n" + "=" * 60)
    print("Testing Rami Levy Scraper...")
    print("=" * 60)
    
    test_products = ["ביצים", "חלב עוף"]
    
    try:
        prices = get_prices_from_rami_levy(test_products)
        
        print(f"\nResults for Rami Levy:")
        for i, (product, price) in enumerate(zip(test_products, prices)):
            print(f"  {product}: {price} NIS per gram")
        
        success = all(p > 0 for p in prices)
        print(f"\nStatus: {'✓ SUCCESS' if success else '✗ FAILED (some prices are 0)'}")
        return success
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("NUTRIOPTIMAL PRICE SCRAPERS - TEST SUITE")
    print("=" * 60)
    print("\nThis test will check if all three price scrapers are working correctly.")
    print("Each scraper will be tested with 2 sample products.")
    print("\nNote: This process may take 1-2 minutes as it loads real websites.")
    print("Please wait...\n")
    
    results = {
        "Shufersal": test_shufersal(),
        "Victory": test_victory(),
        "Rami Levy": test_rami_levy()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for scraper, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{scraper:15} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} scrapers working")
    
    if total_passed == total_tests:
        print("\n🎉 All scrapers are working correctly!")
        print("You can now run the main application with: python app.py")
    else:
        print("\n⚠️  Some scrapers failed. Check the errors above for details.")
    
    return total_passed == total_tests


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)