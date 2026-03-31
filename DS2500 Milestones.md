# Introductory ideas

| If we learn | Then people could | Which might lead to |
| ----- | ----- | ----- |
| Businesses in certain neighborhoods stay around longer | Seek better loans for new businesses in that area | Better loan rates for new business owners |
| Neighborhood business tax rate increases cause businesses to close | Dispute the raising of neighborhood business taxes | Longevity of small businesses in boston |
| A certain business type stays around longer | Open a business of that type | $$$ |
| Two business types when connected are more successful | Partner to open a business, invest safely in secondary businesses | $$$ |
| Mixed use buildings are more successful | Architects/city designers could build/establish more mixed use areas | More business more money city productivity |

FOR MILESTONE 1 QUESTION 5:   
**\*\*MAKE SURE ALL DATA SETS ARE IN THE FORMAT IN A CSV FILE\*\***  
**\*\*PROF SAID THAT THE DATA SETS DON’T HAVE TO BE PERFECT, DON’T SPEND TOO MUCH TIME ON THIS\*\***

Sources:

Massachusetts Open Data \- **Massachusetts Business Registry \- Employment & Wage Data (ES-202) \- Economic Census (state-level extracts)**  
[MassGIS Data Hub](https://gis.data.mass.gov/)

MA Corporations Search  
[https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx](https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx)

- For chain businesses

[https://data.boston.gov/](https://data.boston.gov/)

- Homepage link we can find other sources through it 

[https://medium.com/data-science/foods-around-me-google-maps-data-scraping-with-python-google-colab-588986c63db3](https://medium.com/data-science/foods-around-me-google-maps-data-scraping-with-python-google-colab-588986c63db3)

Boston Report on Small Businesses (pdf, with additional sources) ([https://www.boston.gov/sites/default/files/document-file-07-2018/160330\_boston\_small\_business\_full\_report\_-\_web\_144dpi\_tcm3-53060.pdf](https://www.boston.gov/sites/default/files/document-file-07-2018/160330_boston_small_business_full_report_-_web_144dpi_tcm3-53060.pdf))

- Pdf of statistics   
- Try to find the data source the pdf pulled from  
  Primary sources:  
- Surveys of small business owners (project/business survey data is referenced, e.g., insights on challenges in certain neighborhoods or BSO-scarce areas).  
- Stakeholder interviews and focus groups (with business owners, residents, community organizations, city staff, and others).  
- Engagement with various organizations and individuals across Boston.  
  Secondary sources:  
- U.S. Census Bureau data (e.g., Economic Census, County Business Patterns for business counts by industry/neighborhood).  
- U.S. Small Business Administration (SBA) statistics.  
- Local administrative data from the City of Boston or Massachusetts state sources.  
- Consumer spending or economic indicators from sources like Esri or similar (though not confirmed here).

**MILESTONE 2 TIMELINE**

| Week 1 \- March 9 | Data Collection |
| :---- | :---- |
| Week 2 \- March 16 | Data Cleaning |
| Week 3 \- March 23 | Initial EDA |
| Week 4 \- March 30Milestone 3 due Tues, March 31 | EDA \+ visualization, modeling |
| Week 5 \- April 6 | Presentation prep |
| Week 6 \- April 13 Milestone 4 due Mon, April 13 Presentation on Tues, April 14 OR Fri, April 17 (TBD) | Final edits, presentation practice |

Get rid of repeat businesses. Find more data to work with.   

# Milestone 1 due Feb 20

**Question 1: What is your team’s section?**  
Your section: Data Science 2500 Section 01 

**Question 2: Who are your team members?**  
Name 1: Tula Hionas  
Name 2: Taylor Dunn  
Name 3: Addison Apisarnthanarax  
Name 4: Abby Rillovick 

**Question 3: What are you trying to do? (problem or topic) Describe in a couple sentences**  
We’ll seek to answer the question: what affects storefront business success in Boston?  
We will analyze how independent factors such as location (neighborhood/district), business type (restaurant, retail, service, etc.), and national chain/multiple locations influence longevity and whether the business is still open. 

**Question 4: Why is this important? Short summary (2-3 sentences) of who cares about**  
**this problem, what impact it has, what implications better solutions might have.**  
Current small business owners seeking to expand, people looking to start new businesses, investors and lenders (angel investors, VCs, banks) evaluating risk, city government tracking tax revenue streams, and property developers planning mixed-use projects all need to understand what drives storefront success in Boston.  
Better predictions of business longevity could help entrepreneurs make smarter location and business type decisions, enable financial institutions to offer fairer loan terms in undervalued areas, and guide urban planners toward mixed-use development strategies that foster economic vitality.  
If certain neighborhoods, business types, or configurations (like mixed-use buildings or complementary business pairings) consistently show higher success rates, this knowledge could reduce small business failure rates, strengthen neighborhood economies, and inform data-driven policy decisions about zoning, taxation, and economic development incentives.

**Question 5: What dataset(s) are you interested in working with? Add links if possible.**  
'Doing Business As' (DBA) Database Search ([https://www.cityofboston.gov/cityclerk/dbasearch/](https://www.cityofboston.gov/cityclerk/dbasearch/))

- Some businesses don't have renewal dates.  
- Issue/expiration date increments don’t actually tell how long the business is around. Initial file date, renewal date, and projected expiration \~4 year accuracy

Google Places API [https://developers.google.com/maps/documentation/places/web-service](https://developers.google.com/maps/documentation/places/web-service)

Property Assessment Data for Boston, MA v. 2020  
[https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/O2ADLG](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/O2ADLG)

- Mostly helpful for tax evaluation aspect

[https://data.boston.gov/dataset/licensing-board-licenses](https://data.boston.gov/dataset/licensing-board-licenses)

- For food and drink licenses.

[https://www.hiddenboston.com/closings-openings.html\#google\_vignette](https://www.hiddenboston.com/closings-openings.html#google_vignette)

- For newly opened and newly closed restaurants in Boston by month and year

# Milestone 2 due Mar 10

Data Science 2500 \- Milestone 2   
10 March 2026

Tula Hionas([hionas.t@northeastern.edu](mailto:hionas.t@northeastern.edu))  
Abigail Rillovick([rillovick.a@northeastern.edu](mailto:rillovick.a@northeastern.edu))  
Addison Apisarnthanarax([apisarnthanarax.a@northeastern.edu](mailto:apisarnthanarax.a@northeastern.edu))  
Taylor Dunn([dunn.tay@northeastern.edu](mailto:dunn.tay@northeastern.edu)) 

**Proposal Statement**  
We’ll seek to answer the question: what affects storefront business success in Boston? We will analyze how independent factors such as location (neighborhood/district), business type (restaurant, retail, service, etc.), and national chain/multiple locations influence longevity and whether the business is still open.  
**Data Sources**  
The data for this project will be a compilation from a few sources to verify business information and supplement missing data. Using a number of different sources, including both official business filings from city government websites and crowd-sourced data. For the framework of our data set we’ll use the ‘Doing Business As’ database[^1] to provide a foundation of existing businesses in Boston, including data for neighborhood, business type, opening date. Google Datasets API[^2] will be used to support or revise findings for the business location, as well as possible “years in business” labels. Boston property assessment data[^3] will be used for understanding tax evaluation brackets, contributing to the business finances angle. Many storefront businesses sell food and drink, and information regarding the required licenses for these sales can be found in the Boston board licenses database[^4].   
While all this information is publicly available, it could contain privacy violations especially for the smaller businesses. Some businesses may run out of a home, so their business address is the same as an individual’s home address. Some small business owners register their businesses at their home address. We will not publish or abuse this information, and we will use google maps or any storefront address to correct this difference. The learnings from this dataset, especially around use for lenders, could further disenfranchise business owners in neighborhoods facing financial struggles and increase wealth disparity if they are passed up for a loan because of the statistics of their neighborhood.   
**Analysis goals and general methods**  
We would like to predict which areas have businesses with higher success rates and longevity, enabling entrepreneurs to make smarter decisions when selecting a location for their business, and investors in supporting businesses with a better chance of success. We will do so by using web scraping to select specific pieces of information for each business and/or neighborhood. If time allows, we would like to predict business longevity based on neighborhood location and business type using machine learning models.  
This analysis will also provide insight into other predictions that allow for more informed business type decisions, supporting entrepreneurs, encouraging financial institutions to offer better loans to businesses, and determine factors to stimulate economic vitality.  
**Division of labor**  
	We plan to divide labor by leader and supporter roles for sections of the workload. Every member is interested in learning and improving skills. We will divide leadership as follows:  
Data collection and cleaning will be led by Taylor and Tula, supported by Abby and Addison. This will include collecting information from various sources, cleaning and validating information (removing repeat businesses, null values), presented in a usable form. 2 weeks.  
Exploratory Data Analysis will be led by Abby and Addison, supported by Taylor and Tula. This will include hypothesis testing, analysis, and visualization. Initial analysis/exploration should be done by milestone 3 (Mar 31\) to follow with establishing hypotheses. 2 weeks.  
Data modeling will be led by Addison, supported by Abby, Taylor, and Tula. This will provide a predictive model for future business establishment success. 1-2 weeks.

# Milestone 3 due Mar 31

**Report format**

* Length: 2-3 pages, double-spaced  
* Format: Submit as PDF on Canvas  
* Submission: Only one team member needs to submit for the team (group) on Canvas  
* Review: Your TA will grade and provide feedback


**Required content**  
Clearly specify the names and emails of all team members on the proposal.

Address each section concisely:

1. Progress summary: What has your team accomplished since the proposal? Include any preliminary findings.  
   1. Have you obtained your data sources?  
   2. What algorithms/tools did you use? Include basic dataset statistics and any preliminary results.  
   3. If you used a machine learning method, state which method and how it was implemented (what features were used, what metrics for evaluation).  
2. Current challenges: What obstacles have you encountered and how are you addressing them? Any changes to your original approach?  
3. Team check-in: What did each member do so far for the project? Is your division of labor working? Any role adjustments needed?  
4. Next steps: What major tasks remain and your timeline for completion. Any concerns about meeting deadlines? How would you evaluate the performance of your machine learning model if you are using machine learning? What metrics would you focus on?  
5. Questions: Specific areas where you need instructor/TA guidance.

# Milestone 4 due Apr 13

PRESENTATION\!

# Milestone 5 due Apr 22

# Things to work on

* Data Collection  
  * Add APIs and other data\!  
  * Other business success metrics? Stars from yelp?/ google reviews?  
* Data Cleaning  
  *   
* Initial EDA  
  * Evaluate based on other factors too. Look at clusters of restaurants/businesses  
    * k means clustering based on gps location  
  * Hypothesis  
    * Seaport and new fenway would have many newer businesses, older neighborhoods may have a mix of old and new.  
    * A business of a different type opened near a cluster of businesses will do better (business diversity)  
    * A business of the same type in a neighborhood with a number of that type of business will not do as well because of competition? Like grocery stores. Opposite effect for a restaurant.  
    * There are neighborhoods with greater clusters of restaurants in close vicinity. These are more successful than businesses far from other businesses/restaurants.  
    * **Businesses close to public transportation (train stops) are more successful. Specifically grocery stores.**  
      * **Need gps of t stops.**  
    * Businesses in high density population areas are more successful.  
      * Need dataset of population density/ARCGIS

* EDA \+ visualization, modeling  
  * **Accuracy**  
  * **Precision**  
  * **Recall**  
  * Confusion matrix  
* Presentation prep  
* Final edits, presentation practice

[^1]:  [https://www.cityofboston.gov/cityclerk/dbasearch/](https://www.cityofboston.gov/cityclerk/dbasearch/)

[^2]:  [https://developers.google.com/maps/documentation/datasets/get](https://developers.google.com/maps/documentation/datasets/get)

[^3]:  [https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/O2ADLG](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/O2ADLG)

[^4]:  [https://data.boston.gov/dataset/licensing-board-licenses](https://data.boston.gov/dataset/licensing-board-licenses)