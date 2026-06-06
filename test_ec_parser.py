line = open(
    "/root/Economic_Census_Test/ec3dt02c.txt",
    encoding="utf-8",
    errors="ignore"
).readline()

print("Sector:", line[0:1])
print("State:", line[1:3])
print("District:", line[3:5])
print("Tehsil:", line[5:9])
print("Development Block:", line[9:13])
print("Village/Town:", line[13:17])
print("Activity Code:", line[36:40])
print("Major Activity:", line[40:42])
print("Ownership:", line[44:45])
print("Total Workers:", line[57:63])
print("File Code:", line[98:100])
