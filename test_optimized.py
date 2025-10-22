from data_io.remainder_optimizer import create_enhanced_remainder_groups
from core.models import Rectangle

# Sample data that might cause hanging (adjust based on your data)
# Use larger quantities to test limits
sample_remaining = [
    Rectangle(id=1, width=100, length=200, qty=50),  # Large qty to test limits
    Rectangle(id=2, width=150, length=250, qty=30),
    Rectangle(id=3, width=120, length=180, qty=40),
    Rectangle(id=4, width=80, length=220, qty=25),
    Rectangle(id=5, width=90, length=190, qty=35),
    Rectangle(id=6, width=110, length=210, qty=45),
]

min_width = 200
max_width = 400
tolerance_length = 50

print("Testing create_enhanced_remainder_groups with limits...")
groups, remaining, stats = create_enhanced_remainder_groups(
    sample_remaining, [(min_width, max_width)], tolerance_length
)
print(f"Created {len(groups)} groups.")
print(f"Remaining items: {len(remaining)}")
print(f"Stats: {stats}")
print("Test completed successfully!")
