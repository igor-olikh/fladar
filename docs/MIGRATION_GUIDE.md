# Migration Guide

This guide helps you upgrade Fladar from version 1.0.0 to version 1.1.0.

## Breaking Changes

### Configuration Parameter Change: `max_stops` → `max_stops_person1` and `max_stops_person2`

**What Changed:**
- The single `max_stops` parameter has been replaced with two separate parameters: `max_stops_person1` and `max_stops_person2`
- This allows each person to have different stop preferences (e.g., Person 1: direct flights only, Person 2: up to 2 stops)

**Why This Change:**
- Provides more flexibility for different travel preferences
- Allows one person to prefer direct flights while the other is willing to accept connections
- Better reflects real-world travel planning scenarios

## Migration Steps

### Step 1: Update Your `config.yaml`

**Before (v1.0.0):**
```yaml
search:
  max_stops: 0  # 0 = direct flights only
```

**After (v1.1.0):**
```yaml
search:
  max_stops_person1: 0  # Maximum stops for Person 1 flights
  max_stops_person2: 0  # Maximum stops for Person 2 flights
```

### Step 2: Set Appropriate Values

Decide on stop preferences for each person:

- **Both want direct flights only:**
  ```yaml
  max_stops_person1: 0
  max_stops_person2: 0
  ```

- **Person 1 wants direct, Person 2 accepts 1 stop:**
  ```yaml
  max_stops_person1: 0
  max_stops_person2: 1
  ```

- **Both accept up to 2 stops:**
  ```yaml
  max_stops_person1: 2
  max_stops_person2: 2
  ```

### Step 3: Verify Your Configuration

After updating your `config.yaml`, verify it's correct:

1. Check that both `max_stops_person1` and `max_stops_person2` are present
2. Ensure values are integers (0, 1, 2, etc.)
3. Remove any old `max_stops` parameter if it still exists

### Step 4: Test Your Configuration

Run the application to ensure everything works:

```bash
python main.py
```

Check the output to confirm:
- The application starts without errors
- Search parameters display correctly showing both max_stops values
- Flight searches work as expected

## Backward Compatibility

**Note:** Version 1.1.0 does **not** support the old `max_stops` parameter. If you try to use the old parameter, the application will use default values (0 for both persons), which may not match your intended configuration.

**If you see this warning:**
```
WARNING: Old 'max_stops' parameter detected. Please update to 'max_stops_person1' and 'max_stops_person2'
```

Update your configuration file immediately to use the new parameters.

## Example Migration

### Complete Config Example

**Before (v1.0.0):**
```yaml
origins:
  person1: "TLV"
  person2: "ALC"

search:
  outbound_date: "2025-11-20"
  return_date: "2025-11-25"
  max_price: 600
  max_stops: 0
  arrival_tolerance_hours: 6
```

**After (v1.1.0):**
```yaml
origins:
  person1: "TLV"
  person2: "ALC"

search:
  outbound_date: "2025-11-20"
  return_date: "2025-11-25"
  max_price: 600
  max_stops_person1: 0  # Maximum stops for Person 1 flights
  max_stops_person2: 0  # Maximum stops for Person 2 flights
  arrival_tolerance_hours: 6
```

## Additional Changes in v1.1.0

### Automatic CSV Cleanup
- CSV output files are now automatically deleted at startup
- This prevents confusion from old results
- No configuration changes needed

### Documentation Updates
- All documentation has been updated to reflect the new parameter structure
- See `README.md` and `docs/` folder for updated examples

## Need Help?

If you encounter any issues during migration:

1. Check the [README.md](../README.md) for configuration examples
2. Review [docs/PROJECT_EXPLANATION.md](PROJECT_EXPLANATION.md) for detailed parameter descriptions
3. Check the [CHANGELOG.md](../CHANGELOG.md) for all changes in v1.1.0

## Summary

- ✅ Replace `max_stops` with `max_stops_person1` and `max_stops_person2`
- ✅ Set appropriate values for each person
- ✅ Test your configuration
- ✅ Enjoy the new flexibility!

