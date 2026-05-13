from market_intelligence.storage.gics_repository import GICSRepository

async def normalize_ticker_row(
    symbol: str,
    company_name: str,
    sector_name: str,
    sub_industry_name: str,
    gics_repo: GICSRepository
) -> dict:
    sector_id       = await gics_repo.get_sector_id(sector_name)
    sub_industry_id = await gics_repo.get_sub_industry_id(sub_industry_name)
    industry_id     = await gics_repo.get_industry_id_from_sub_industry(sub_industry_id)
    industry_group_id = await gics_repo.get_industry_group_id_from_industry(industry_id)

    return {
        "symbol":           symbol,
        "company_name":     company_name,
        "sector_id":        sector_id,
        "industry_group_id": industry_group_id,
        "industry_id":      industry_id,
        "sub_industry_id":  sub_industry_id,
    }