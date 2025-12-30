# Testing Guide: Pokemon Name Matching

This guide explains how to test if the Pokemon name matching works correctly for both normal Pokemon and multi-word Pokemon like "Great Tusk".

## Quick Test in the Application

### 1. **Test Normal Single-Word Pokemon**

Type these in the chat and check if sprites appear in the sidebar:

✅ **Should Work:**
- `pikachu`
- `What's the best set for pikachu?`
- `charizard`
- `Show me teams with umbreon`

❌ **Should NOT Work (no sprite should appear):**
- `pika` (should NOT match pikachu)
- `char` (should NOT match charizard)
- `umbr` (should NOT match umbreon)

### 2. **Test Multi-Word Pokemon (Great Tusk)**

Type these variations and check if the Great Tusk sprite appears:

✅ **Should Work:**
- `Great Tusk` (with space)
- `great-tusk` (with hyphen)
- `great tusk` (lowercase with space)
- `What's the best set for Great Tusk?`
- `Show me teams with great-tusk`

❌ **Should NOT Work (no sprite should appear):**
- `great` (should NOT match great-tusk)
- `tusk` (should NOT match great-tusk)
- `Great` (should NOT match great-tusk)

### 3. **What to Look For**

When you type a query:
1. **Check the sidebar** - Pokemon sprites should appear on the left side
2. **Click a sprite** - Should open the Pokemon stat card
3. **Check the console** (if you have it open) - Should see no errors

## Automated Testing

If you want to run automated tests:

### Prerequisites
1. Activate your virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

2. Make sure all dependencies are installed

### Run the Test Script

```bash
python test_pokemon_matching.py
```

This will:
- Test regex patterns directly
- Test the full `get_pokemon_sprite_urls` function
- Show which tests pass or fail

## Manual Testing Checklist

Use this checklist to verify everything works:

### Normal Pokemon Tests
- [ ] Type "pikachu" → Pikachu sprite appears
- [ ] Type "charizard" → Charizard sprite appears
- [ ] Type "pika" → NO sprite appears (correct - substring shouldn't match)
- [ ] Type "char" → NO sprite appears (correct - substring shouldn't match)

### Great Tusk Tests
- [ ] Type "Great Tusk" → Great Tusk sprite appears
- [ ] Type "great-tusk" → Great Tusk sprite appears
- [ ] Type "great tusk" → Great Tusk sprite appears
- [ ] Type "great" → NO sprite appears (correct - partial word shouldn't match)
- [ ] Type "tusk" → NO sprite appears (correct - partial word shouldn't match)

### Edge Cases
- [ ] Type "What's the best set for pikachu?" → Pikachu sprite appears
- [ ] Type "Show me teams with Great Tusk and Umbreon" → Both sprites appear
- [ ] Type "charizard-mega" → Charizard sprite appears (base form)

## Troubleshooting

### If sprites don't appear:
1. Check browser console for JavaScript errors
2. Check Python console/logs for errors
3. Verify the Pokemon name is in `ALL_SPECIES` list
4. Check network tab to see if sprite URLs are being requested

### If wrong Pokemon appear:
1. The matching might be too loose - check the regex patterns
2. Verify word boundaries are working correctly
3. Check if there are similar Pokemon names causing conflicts

### If Great Tusk doesn't work:
1. Verify "great-tusk" is in the `ALL_SPECIES` list
2. Check if sprite filenames match the expected format
3. Test with both space and hyphen variations

## Expected Behavior Summary

| Input | Should Match | Should NOT Match |
|-------|-------------|------------------|
| `pikachu` | ✅ pikachu | ❌ pika, pik |
| `charizard` | ✅ charizard | ❌ char, chariz |
| `Great Tusk` | ✅ great-tusk | ❌ great, tusk |
| `great-tusk` | ✅ great-tusk | ❌ great, tusk |
| `great tusk` | ✅ great-tusk | ❌ great, tusk |
| `great` | ❌ (nothing) | ❌ great-tusk |
| `char` | ❌ (nothing) | ❌ charizard |

