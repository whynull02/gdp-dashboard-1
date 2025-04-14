from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import pandas as pd
from pathlib import Path
from typing import List

app = FastAPI(
    title="GDP API",
    description="World Bank GDP data API"
)

def get_gdp_data():
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    return gdp_df

@app.get("/gdp")
async def get_gdp(
    countries: List[str] = Query(default=['DEU', 'FRA']),
    from_year: int = Query(default=1960),
    to_year: int = Query(default=2022)
):
    gdp_df = get_gdp_data()
    filtered_data = gdp_df[
        (gdp_df['Country Code'].isin(countries))
        & (gdp_df['Year'] <= to_year)
        & (from_year <= gdp_df['Year'])
    ]
    
    return JSONResponse(
        content=filtered_data.to_dict(orient='records')
    )

@app.get("/countries")
async def get_countries():
    gdp_df = get_gdp_data()
    return {"countries": gdp_df['Country Code'].unique().tolist()}

if __name__ == "__main__":
    import uvicorn
    # 모든 IP에서의 접속을 허용하기 위해 host를 0.0.0.0으로 설정
    uvicorn.run(app, host="0.0.0.0", port=8000)
