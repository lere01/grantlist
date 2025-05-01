from .awesome import fetch_awesome
from .nlnet   import fetch_nlnet
from .emergent import fetch_emergent
from .prototype_fund import fetch_prototype
from .openai_credit import fetch_openai_credit
from .moss import fetch_moss
from .gftw import fetch_gftw

SCRAPERS = [fetch_awesome, fetch_nlnet, fetch_emergent, fetch_prototype, fetch_openai_credit, fetch_moss, fetch_gftw]