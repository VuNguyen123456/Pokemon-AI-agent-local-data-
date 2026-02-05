"""
Test script for Pokemon name matching logic.
Tests both normal Pokemon and multi-word Pokemon like "Great Tusk".

To run this test:
1. Activate your virtual environment
2. Run from project root: python tests/test_pokemon_matching.py
   OR from tests directory: python test_pokemon_matching.py
"""
import re
import sys
import os

# Add the parent directory to the path so we can import from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from pokemon_ai import ALL_SPECIES, ALL_FILENAMES, get_pokemon_sprite_urls, SPRITE_BASE_URL
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("\nMake sure you:")
    print("1. Are in the project directory")
    print("2. Have activated your virtual environment")
    print("3. Have installed all dependencies")
    sys.exit(1)

def test_matching_logic():
    """Test the Pokemon matching logic with various inputs."""
    
    print("=" * 60)
    print("Testing Pokemon Name Matching Logic")
    print("=" * 60)
    print()
    
    # Test cases: (input_text, expected_matches, should_not_match)
    test_cases = [
        # Normal single-word Pokemon
        ("pikachu", ["pikachu"], ["pika", "pik"]),
        ("charizard", ["charizard"], ["char", "chariz"]),
        ("What's the best set for pikachu?", ["pikachu"], ["pika"]),
        
        # Multi-word Pokemon - Great Tusk
        ("Great Tusk", ["great-tusk"], ["great", "tusk"]),
        ("great-tusk", ["great-tusk"], ["great", "tusk"]),
        ("great tusk", ["great-tusk"], ["great", "tusk"]),
        ("Show me teams with Great Tusk", ["great-tusk"], ["great", "tusk"]),
        ("What's the best set for great-tusk?", ["great-tusk"], ["great", "tusk"]),
        
        # Edge cases - should NOT match
        ("char", [], ["charizard"]),  # "char" should not match "charizard"
        ("pika", [], ["pikachu"]),  # "pika" should not match "pikachu"
        ("great", [], ["great-tusk"]),  # "great" alone should not match "great-tusk"
        ("tusk", [], ["great-tusk"]),  # "tusk" alone should not match "great-tusk"
    ]
    
    print("Test Results:")
    print("-" * 60)
    
    all_passed = True
    
    for i, (input_text, expected_matches, should_not_match) in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{input_text}'")
        print(f"  Expected to match: {expected_matches}")
        print(f"  Should NOT match: {should_not_match}")
        
        # Get actual matches using the function
        try:
            result = get_pokemon_sprite_urls(
                text=input_text,
                all_species=ALL_SPECIES,
                all_filenames=ALL_FILENAMES,
                sprite_base_url=SPRITE_BASE_URL,
                max_pokemon=6
            )
            
            # Extract matched species names from result
            matched_species = []
            for sprite_list in result:
                if sprite_list:
                    # Extract Pokemon name from first sprite URL
                    # Format: "https://.../{pokemon-name}-{form}.png"
                    first_sprite = sprite_list[0]
                    pokemon_name = first_sprite.split('/')[-1].split('-')[0]
                    matched_species.append(pokemon_name.lower())
            
            print(f"  Actual matches: {matched_species}")
            
            # Check if expected matches are present
            passed = True
            for expected in expected_matches:
                # Normalize expected name (remove hyphens/spaces for comparison)
                expected_normalized = expected.replace('-', '').replace(' ', '')
                found = False
                for matched in matched_species:
                    matched_normalized = matched.replace('-', '').replace(' ', '')
                    if expected_normalized == matched_normalized:
                        found = True
                        break
                if not found:
                    print(f"  ❌ FAILED: Expected '{expected}' but not found")
                    passed = False
                    all_passed = False
            
            # Check if should_not_match items are NOT present
            for should_not in should_not_match:
                should_not_normalized = should_not.replace('-', '').replace(' ', '')
                for matched in matched_species:
                    matched_normalized = matched.replace('-', '').replace(' ', '')
                    if should_not_normalized in matched_normalized or matched_normalized in should_not_normalized:
                        print(f"  ❌ FAILED: Should NOT match '{should_not}' but found '{matched}'")
                        passed = False
                        all_passed = False
            
            if passed:
                print(f"  ✅ PASSED")
            else:
                all_passed = False
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            all_passed = False
    
    print()
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)
    
    return all_passed


def test_direct_regex():
    """Test the regex patterns directly for debugging."""
    print("\n" + "=" * 60)
    print("Direct Regex Pattern Testing")
    print("=" * 60)
    print()
    
    test_inputs = [
        "pikachu",
        "charizard",
        "Great Tusk",
        "great-tusk",
        "great tusk",
        "char",  # Should NOT match charizard
        "pika",  # Should NOT match pikachu
        "great",  # Should NOT match great-tusk
    ]
    
    # Test with a few known Pokemon
    test_species = ["pikachu", "charizard", "great-tusk"]
    
    for test_input in test_inputs:
        print(f"Input: '{test_input}'")
        text_lower = test_input.lower()
        
        for species in test_species:
            name = species.lower()
            has_separator = ' ' in name or '-' in name
            
            matches = False
            
            if has_separator:
                name_with_space = name.replace('-', ' ')
                name_with_hyphen = name.replace(' ', '-')
                
                patterns = [
                    r'\b' + re.escape(name) + r'\b',
                    r'\b' + re.escape(name_with_space) + r'\b',
                    r'\b' + re.escape(name_with_hyphen) + r'\b',
                ]
                
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        matches = True
                        print(f"  ✅ Matches '{species}' (pattern: {pattern})")
                        break
            else:
                pattern = r'\b' + re.escape(name) + r'\b'
                if re.search(pattern, text_lower):
                    matches = True
                    print(f"  ✅ Matches '{species}' (pattern: {pattern})")
        
        if not matches:
            print(f"  ❌ No matches")
        print()


if __name__ == "__main__":
    # Run direct regex tests first (faster)
    test_direct_regex()
    
    # Then run full function tests
    print("\n" + "=" * 60)
    print("Running Full Function Tests (this may take a moment)...")
    print("=" * 60)
    test_matching_logic()

