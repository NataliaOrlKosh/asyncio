import aiohttp
import asyncio

from models import Character, get_async_session

SW_API = 'https://swapi.dev/api/people/'


async def get_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response = await response.json()
        await session.close()
    return response


async def get_detail_names(json, detail, key):
    detail_requests = [get_page(url) for url in json[detail]]
    results = await asyncio.gather(*detail_requests)
    names = [res[key] for res in results]
    return ', '.join(names)


async def get_homeworld(json):
    res = await get_page(json['homeworld'])
    return res['name']


async def get_character_data():
    session = get_async_session()
    characters_tasks = [asyncio.create_task(get_page(f'{SW_API}{i}')) for i in range(100)]
    characters = await asyncio.gather(*characters_tasks)
    for character in characters:
        if character.get('detail') is None:
            detail_tasks = []
            films = asyncio.create_task(get_detail_names(character, 'films', 'title'))
            detail_tasks.append(films)
            homeworld = asyncio.create_task(get_homeworld(character))
            detail_tasks.append(homeworld)
            species = asyncio.create_task(get_detail_names(character, 'species', 'name'))
            detail_tasks.append(species)
            starships = asyncio.create_task(get_detail_names(character, 'starships', 'name'))
            detail_tasks.append(starships)
            vehicles = asyncio.create_task(get_detail_names(character, 'vehicles', 'name'))
            detail_tasks.append(vehicles)
            detail_res = await asyncio.gather(*detail_tasks)
            new_char = Character(pers_id=int(character['url'].split('/')[-2]),
                                 birth_year=character['birth_year'],
                                 eye_color=character['eye_color'],
                                 films=detail_res[0],
                                 gender=character['gender'],
                                 hair_color=character['hair_color'],
                                 height=character['height'],
                                 homeworld=detail_res[1],
                                 mass=character['mass'],
                                 name=character['name'],
                                 skin_color=character['skin_color'],
                                 species=detail_res[2],
                                 starships=detail_res[3],
                                 vehicles=detail_res[4]
                                 )
            session.add(new_char)
            await session.commit()


if __name__ == '__main__':
    asyncio.run(get_character_data())
