# Flight Results Explanation Guide

This document explains how to read and understand the flight results in the CSV output file.

## Understanding the CSV Structure

The CSV file contains flight options where **two people meet at the same destination**. Each row represents one complete travel plan with flights for both Person 1 and Person 2.

---

## Top 5 Flights Explained

### Flight #1: Barcelona (BCN) - Total: €502.48

**Meeting Destination:** Barcelona, Spain (BCN)

**Total Cost:** €502.48
- Person 1 (from Alicante): €157.66
- Person 2 (from Tel Aviv): €344.82

#### Person 1 (ALC → BCN → ALC) - €157.66

**OUTBOUND FLIGHT (Going to Barcelona):**
- **Departure:** November 20, 2025 at 20:45 UTC (21:45 local time in Alicante/Paris timezone)
- **Arrival:** November 21, 2025 at 16:35 UTC (17:35 local time in Barcelona/Paris timezone)
- **Duration:** 19 hours 50 minutes (PT19H50M)
- **Airline:** UX (Air Europa)
- **Note:** This is an overnight flight with a long layover or connection

**RETURN FLIGHT (Coming back from Barcelona):**
- **Departure:** November 25, 2025 at 22:00 UTC (23:00 local time in Barcelona)
- **Arrival:** November 26, 2025 at 11:40 UTC (12:40 local time in Alicante)
- **Duration:** 13 hours 40 minutes (PT13H40M)
- **Airline:** UX (Air Europa)

#### Person 2 (TLV → BCN → TLV) - €344.82

**OUTBOUND FLIGHT (Going to Barcelona):**
- **Departure:** November 20, 2025 at 15:55 UTC (17:55 local time in Tel Aviv/Jerusalem timezone)
- **Arrival:** November 21, 2025 at 17:05 UTC (18:05 local time in Barcelona)
- **Duration:** 26 hours 10 minutes (PT26H10M) - includes layover/connection
- **Airline:** AF (Air France)

**RETURN FLIGHT (Coming back from Tel Aviv):**
- **Departure:** November 25, 2025 at 20:20 UTC (21:20 local time in Barcelona)
- **Arrival:** November 26, 2025 at 14:15 UTC (16:15 local time in Tel Aviv)
- **Duration:** 16 hours 55 minutes (PT16H55M)
- **Airline:** AF (Air France)

**Meeting Time:** Both people arrive in Barcelona on November 21, 2025:
- Person 1 arrives at 17:35 (Barcelona time)
- Person 2 arrives at 18:05 (Barcelona time)
- **They meet within 30 minutes of each other!** ✅

---

### Flight #2: Barcelona (BCN) - Total: €504.11

**Total Cost:** €504.11
- Person 1: €159.29
- Person 2: €344.82

**Difference from Flight #1:** Person 1's return flight departs earlier (15:30 instead of 22:00), making the return trip longer (20 hours 10 minutes instead of 13 hours 40 minutes).

---

### Flight #3: Barcelona (BCN) - Total: €513.47

**Total Cost:** €513.47
- Person 1: €157.66
- Person 2: €355.81

**Difference from Flight #1:** Person 2's return flight is more expensive and departs earlier (18:05 instead of 20:20).

---

### Flight #4: Barcelona (BCN) - Total: €513.47

**Total Cost:** €513.47
- Person 1: €157.66
- Person 2: €355.81

**Difference from Flight #3:** Person 2's return flight departs even earlier (16:00 instead of 18:05), making it a longer trip (21 hours 15 minutes).

---

### Flight #5: Barcelona (BCN) - Total: €513.47

**Total Cost:** €513.47
- Person 1: €157.66
- Person 2: €355.81

**Difference from Flight #4:** Person 2's return flight departs at 15:05, making it the longest return trip (22 hours 10 minutes).

---

## Key Terms Explained

### Route Column
- **Format:** "ALC & TLV → BCN"
- **Meaning:** Both people (from Alicante and Tel Aviv) meet in Barcelona

### Outbound vs Return
- **Outbound:** The flight TO the destination (going to meet)
- **Return:** The flight FROM the destination (coming back home)

### Time Formats
- **UTC Time:** Universal Coordinated Time (standard time reference)
- **Local Time:** Time in the specific city's timezone
  - `local_tlv` = Tel Aviv/Jerusalem time
  - `local_alc` = Alicante/Madrid time
  - `local_dest` = Destination city time (Barcelona in these examples)

### Duration Format
- **PT19H50M** = Period Time: 19 Hours, 50 Minutes
- This includes all flight time, layovers, and connections

### Airlines
- **UX** = Air Europa
- **AF** = Air France
- Multiple airlines means you'll have connections/layovers

---

## How to Read a Flight Option

1. **Check the destination** - Where will you meet?
2. **Check total price** - Is it within your budget?
3. **Check arrival times** - Do both people arrive close to each other? (within your tolerance window)
4. **Check departure times** - Do they meet your "not earlier than" requirements?
5. **Check duration** - Are you okay with the flight length?
6. **Check airlines** - Do you have preferences?

---

## Important Notes

### Meeting Time Window
The application ensures both people arrive within a specified time window (default: ±6 hours). In the examples above, Person 1 and Person 2 arrive within 30 minutes of each other, which is excellent!

### Long Durations
Some flights show very long durations (19-26 hours). This usually means:
- The flight has connections/layovers
- It's not a direct flight
- You may need to change planes at an intermediate airport

### Price Differences
Person 2 (from Tel Aviv) typically pays more because:
- Tel Aviv is farther from Barcelona than Alicante
- Longer flights cost more
- Different airlines have different pricing

### Time Zones
Always check the **local times** when planning:
- When you need to be at the airport
- When you'll arrive at your destination
- When you'll be back home

---

## Tips for Choosing a Flight

1. **Best Value:** Flight #1 (€502.48) - Lowest total price
2. **Best Arrival Times:** Check which flights have arrivals closest together
3. **Shortest Duration:** Look for flights with shorter duration (PT values)
4. **Direct Flights:** If `max_stops: 0` in config, all flights are direct (no connections)
5. **Return Convenience:** Consider when you want to return - earlier flights may be cheaper but longer

---

## Example: Planning Your Trip

Using **Flight #1** as an example:

**November 20, 2025:**
- Person 1 leaves Alicante at 21:45 (local time)
- Person 2 leaves Tel Aviv at 17:55 (local time)

**November 21, 2025:**
- Person 1 arrives Barcelona at 17:35 (local time)
- Person 2 arrives Barcelona at 18:05 (local time)
- **You meet in Barcelona!** 🎉

**November 25, 2025:**
- Both leave Barcelona (Person 1 at 23:00, Person 2 at 21:20)

**November 26, 2025:**
- Person 1 arrives back in Alicante at 12:40 (local time)
- Person 2 arrives back in Tel Aviv at 16:15 (local time)

---

## Questions?

If you need help understanding any specific flight option, check:
- The `route` column to see the meeting destination
- The `total_price_eur` to see the total cost
- The local time columns to see when things happen in your timezone
- The duration columns to see how long each flight takes

