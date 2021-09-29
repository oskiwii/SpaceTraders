import asyncio
from spacetraders import client

client = client.Client('eb085f34-e8f1-4a5a-93ab-f9c337749dce') # Set token


async def main():
    await asyncio.sleep(3)
    profile = await client.profile()
    profile = await client.profile()
    profile = await client.profile()
    profile = await client.profile()
    profile = await client.profile()
    
    print(profile.credits)
    print(profile.joinedAt)
    print(profile.shipCount)
    print(profile.structureCount)
    print(profile.username)

    status = await client.serverStatus()
    print(status)

    leaderboard = await client.getLeaderboard()
    for entry in leaderboard:
        print(f'\n{entry.username}:\n    - Net Worth: {entry.netWorth}\n   - Rank: {entry.rank}\n')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
