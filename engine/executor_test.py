from executor import SQLExecutor

def main():
    """Test SQLExecutor functionality"""
    executor = SQLExecutor()

    # test_query = """SELECT * FROM public.admin_users LIMIT 5"""
    # test_query = """SELECT * FROM districts WHERE district_uid = '209';"""
    test_query = """SELECT b.block_name 
FROM blocks b
JOIN blocks_sub_division_lnk bsd ON b.id = bsd.block_id
JOIN sub_divisions_district_lnk sdd ON bsd.sub_division_id = sdd.sub_division_id
JOIN districts d ON sdd.district_id = d.id
WHERE d.district_uid = '217'
ORDER BY b.block_name ASC"""

    print(f"\nExecuting Query:\n{test_query}")
    
    success, results, formatted_results, error = executor.main_executor(test_query)
    
    if success:
        print(f"\nSuccess! Found {len(results)} rows")
        print("\nFormatted Results:")
        print(formatted_results)
        print("\nRaw Results:")
        print(results)
    else:
        print(f"\nFailed: {error}")

if __name__ == "__main__":
    main() 