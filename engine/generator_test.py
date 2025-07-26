from generator import SQLGenerator

def main():
    """Test SQL generation functionality"""
    generator = SQLGenerator()
    
    # Test query
    query = """FPS Inspection Report for the following parameters:
{
    "startDate": "2025-05-01",
    "endDate": "2025-05-06",
}"""
    
    print("\nTesting SQL Generator:")
    print(f"\nQuery: '{query}'")
    
    try:
        # Generate SQL
        results = generator.main_generator(query)
        
        print("\nGenerated SQL:")
        print(results['generated_sql'])
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 