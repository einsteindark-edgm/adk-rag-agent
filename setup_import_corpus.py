#!/usr/bin/env python
"""Setup script to create the import_export corpus for Colombian import regulations."""

import asyncio
from a2a_client import RAGAgentClient

async def setup_corpus():
    """Create and configure the import_export corpus."""
    client = RAGAgentClient()
    
    try:
        await client.connect()
        print("✅ Connected to Colombian Import Specialist\n")
        
        # Check existing corpora
        print("📋 Checking existing corpora...")
        response = await client.send_message("List all available corpora")
        print(f"Response: {response}\n")
        
        # Create import_export corpus if needed
        print("📦 Creating import_export corpus...")
        response = await client.send_message("Create a new corpus called import_export")
        print(f"Response: {response}\n")
        
        # Instructions for adding the rules_imports document
        print("📄 Next Steps:")
        print("1. Upload your 'rules_imports' document to Google Drive")
        print("2. Make it accessible (shareable link)")
        print("3. Use the following command to add it to the corpus:")
        print("\n   await client.send_message(")
        print("       \"Add data to import_export from ['YOUR_GOOGLE_DRIVE_URL']\"")
        print("   )\n")
        print("Example Google Drive URL format:")
        print("   https://drive.google.com/file/d/FILE_ID/view")
        print("\nThe document should contain official Colombian import regulations,")
        print("procedures, requirements, tariffs, and restricted items information.")
        
        # Get corpus info
        print("\n📊 Checking import_export corpus info...")
        response = await client.send_message("Get information about import_export")
        print(f"Response: {response}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()

async def test_queries():
    """Test some import-related queries."""
    client = RAGAgentClient()
    
    try:
        await client.connect()
        print("\n🔍 Testing Import Queries:")
        print("=" * 60)
        
        queries = [
            "What are the general import requirements for Colombia?",
            "What documents are typically needed for customs clearance?",
            "Are there any prohibited items for import to Colombia?",
            "How are import duties calculated in Colombia?"
        ]
        
        for query in queries:
            print(f"\nQ: {query}")
            response = await client.send_message(query)
            print(f"A: {response}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()

def main():
    """Main entry point."""
    print("🚢 Colombian Import Specialist - Corpus Setup")
    print("=" * 60)
    print("This script helps you set up the import_export corpus")
    print("for Colombian import regulations.\n")
    
    # Run setup
    asyncio.run(setup_corpus())
    
    # Optional: Test queries
    test = input("\nWould you like to test some queries? (y/n): ")
    if test.lower() == 'y':
        asyncio.run(test_queries())
    
    print("\n✅ Setup complete!")
    print("The agent is now ready to answer Colombian import questions.")
    print("Make sure to add the 'rules_imports' document to the corpus.")

if __name__ == "__main__":
    main()