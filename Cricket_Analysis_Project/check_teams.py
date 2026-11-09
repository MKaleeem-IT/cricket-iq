import pandas as pd

# Load women's international data
df = pd.read_csv('data/womens_international_t20.csv')

# Teams from upcoming fixtures
teams = [
    'Rwanda Women', 'United States Of America Women',
    'Namibia Women', 'Uganda Women',
    'Sri Lanka Women', 'Ireland Women',
    'Papua New Guinea Women', 'Scotland Women',
    'Pakistan Women', 'Bangladesh Women',
    'Netherlands Women', 'Thailand Women'
]

print("=" * 60)
print("TEAM DATA CHECK")
print("=" * 60)

# All unique teams in dataset
all_teams = sorted(set(df['team1'].dropna()) | set(df['team2'].dropna()))
print(f"\nTotal unique teams in dataset: {len(all_teams)}")
print("\nAll teams:")
for t in all_teams:
    print(f"  - {t}")

print("\n" + "=" * 60)
print("UPCOMING TEAMS vs DATASET")
print("=" * 60)

for t in teams:
    count = len(df[(df['team1'] == t) | (df['team2'] == t)])
    status = "✅" if count >= 2 else "❌"
    print(f"{status} {t}: {count} matches")

print("\n" + "=" * 60)
print("RECENT RESULTS CHECK")
print("=" * 60)

try:
    recent = pd.read_csv('mens_t20_data/prepared_recent_results.csv')
    print(f"Total recent results: {len(recent)}")
    print("\nFirst 10 rows:")
    print(recent.head(10).to_string())
except FileNotFoundError:
    print("❌ File not found: mens_t20_data/prepared_recent_results.csv")
except Exception as e:
    print(f"❌ Error: {e}")