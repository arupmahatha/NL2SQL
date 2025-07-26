from entity_extractor import EntityExtractor

def main():
    """Test EntityExtractor functionality"""
    extractor = EntityExtractor()
    
    # Test query
    test_query = """SELECT d.name district_name, sd.name sub_division, b.name block, f.id shop_id, is.scheduled_date 
FROM inspection_schedulings is 
JOIN inspection_schedulings_fps_id_lnk isf ON is.id = isf.inspection_scheduling_id 
JOIN fair_price_shops f ON isf.fair_price_shop_id = f.id 
JOIN fair_price_shops_village_lnk fv ON f.id = fv.fair_price_shop_id 
JOIN villages v ON fv.village_id = v.id 
JOIN blocks b ON v.block_id = b.id 
JOIN sub_divisions sd ON b.sub_division_id = sd.id 
JOIN districts d ON sd.district_id = d.id 
WHERE d.id = 220 
ORDER BY is.scheduled_date"""
    
    print("\nTesting Entity Extractor:")
    print(f"\nTest Query: {test_query}")
    
    try:
        # Extract entities
        entities = extractor.main_entity_extractor(test_query)
        
        print("\nExtracted Entities:")
        if entities:
            for entity in entities:
                print("---")
                print(f"Table: {entity['table']}")
                print(f"Column: {entity['column']}")
                print(f"Value: {entity['value']}")
        else:
            print("No entities were extracted")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 