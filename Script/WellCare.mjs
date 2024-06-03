import fetch from 'node-fetch';
import { JSDOM } from 'jsdom';
import { promises as fs } from 'fs';
import admin from 'firebase-admin';

// Initialize Firebase
import serviceAccount from './wellCareKey.json' assert { type: "json" };

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});
const db = admin.firestore();

// Function to fetch request verification token
async function fetchRequestVerificationToken() {
  const response = await fetch('https://wellcare.isf.io/2024/g/f010acf28d0e468cb2aa59e0e68d694b/Quote/GetQuotePartial', {
    method: 'GET',
    headers: {
      'Accept': 'text/html',
      'X-Requested-With': 'XMLHttpRequest',
    }
  });

  const text = await response.text();
  const dom = new JSDOM(text);

  const token = dom.window.document.querySelector('input[name="__RequestVerificationToken"]').value;
  return token;
}

// Function to get plan data
async function getPlanData(zipCode, countyName, stateAbbreviation, fipsCode, token) {
  const stateFipsCode = fipsCode.slice(0, 2);

  const headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': '_gcl_au=1.1.2020630245.1719605110; invoca_session=%7B%22ttl%22%3A%222024-07-28T20%3A05%3A10.845Z%22%2C%22session%22%3A%7B%7D%2C%22config%22%3A%7B%22ce%22A true%2C%22fv%22A true%7D%7D; _fbp=fb.1.1719605111194.350584963271778211; _ce.irv=new; cebs=1; _ce.s=v~b74d33180398624120fc303fa287cffa5a3c0b26~lcw~1719605111211~lva~1719605111211~vpv~0~lcw~1719605111213; _gid=GA1.2.270489795.1719836108; _clck=1nid4l2%7C2%7Cfn3%7C0%7C1640; _ce.clock_data=16%2C38.122.14.76%2C1%2C10f9287deaf609ee36fb37783f2b89c0%2CChrome%2CUS; _ga_J79ERXWWW5=GS1.2.1719845309.4.0.1719845349.0.0.0; UseNewDesignFeature=False; .AspNetCore.Culture=c%3Den-US%7Cuic%3Den-US; AspNetCore_Session_Cookie=CfDJ8HAEUs1AUs1NvxqdTq8XexaAQzEubvRGw99geCS18kJIumocrYceAE8Q3%2Fz1G5xUUwyBKzZgv2rZhixhjsqeZjeKNiSdSdVaSvLGh4XEuFBhtiTOnadb%2B97AZAZQxNdt1ZYSacLoJ11HoYiXEKX27DvW8Ec56erSXPTFAIz9FpIR; .AspNetCore.Antiforgery.9Ldf4oLyS6k=CfDJ8HAEUs1AUs1NvxqdTq8XexZzvsiCSkqK28qygeBtFz914qBqE0CPxehwX3nlMzC6tF33QvbaiKVxaDLusSrgDOXFnHXzxwDJJ1MPzDuabAP_eouNoLmFVQv2ZQM9d-UTAVOjiWHeGE9IY22gNGm89Cc; _ga_2P7LX36Q85=GS1.1.1719857091.7.1.1719857743.0.0.0; _ga=GA1.2.2013862579.1719605110; _gat_UA-179700527-1=1; _uetsid=8e9ac66037a311ef84b6459da3dce797; _uetvid=b92f45b0358911ef9c6db55e7d33790b; _clsk=1iep2st%7C1719857749160%7C10%7C1%7Cf.clarity.ms%2Fcollect; _gat_UA-43803870-1=1; _ga_GDQD34846P=GS1.1.1719857092.6.1.1719857800.1.0.0; _ga_XNQEBXVC3J=GS1.1.1719857092.6.1.1719857800.1.0.0'
  };

  const payload = new URLSearchParams({
    'quote.Location.Zip': zipCode,
    'quote.Location.County': countyName,
    'quote.Location.State': stateAbbreviation,
    'quote.Location.CountyFipsCode': fipsCode,
    'quote.Location.StateFipsCode': stateFipsCode,
    '__RequestVerificationToken': token
  });

  try {
    const response = await fetch(
      'https://wellcare.isf.io/2024/g/f010acf28d0e468cb2aa59e0e68d694b/Quote/GetQuotePartial',
      {
        method: 'POST',
        headers: headers,
        body: payload.toString()
      }
    );

    const text = await response.text();
    const dom = new JSDOM(text);

    const scriptTags = dom.window.document.querySelectorAll('script');
    let plansJsonString = null;

    scriptTags.forEach(script => {
      if (script.textContent.includes('var plans =')) {
        plansJsonString = script.textContent.match(/var plans = (\[.*?\]);/)[1];
      }
    });

    if (!plansJsonString) {
      console.log(`No plans data found in response for Zip Code: ${zipCode}`);
      return [];
    }

    const plans = JSON.parse(plansJsonString);
    const planElements = dom.window.document.querySelectorAll('.list-col');
    const planDetails = Array.from(planElements).map(el => {
      const name = el.querySelector('h3')?.textContent.trim();
      const contractId = el.querySelector('.section-block p')?.textContent.trim();
      return { name, contractId };
    });

    if (planDetails.length === 0) {
      console.log(`No plan details found in response for Zip Code: ${zipCode}`);
      return [];
    }

    const planData = planDetails.map(detail => {
      const plan = plans.find(p => `${p.Contract}-${p.PbpId}` === detail.contractId);
      if (!plan) {
        return null;
      }
      return {
        productContractCode: `${plan.Contract}-${plan.PbpId}-${plan.SegmentId}`,
        zipCode: zipCode,
        rating: plan.StarRating === 0 ? null : plan.StarRating,
        planName: detail.name,
        planID: plan.PlanId
      };
    }).filter(plan => plan !== null);

    if (planData.length === 0) {
      console.log(`No matching plans found for Zip Code: ${zipCode}`);
      return [];
    }

    for (const plan of planData) {
      try {
        const detailResponse = await fetch(`https://wellcare.isf.io/2024/g/f010acf28d0e468cb2aa59e0e68d694b/Plan/Index?PlanId=${plan.planID}&FormId=${plan.FormId}`, {
          method: 'GET',
          headers: headers
        });
        const detailText = await detailResponse.text();
        const detailDom = new JSDOM(detailText);

        const evidenceLinkElement = Array.from(detailDom.window.document.querySelectorAll('a')).find(a => a.textContent.includes('Evidence of Coverage'));
        if (evidenceLinkElement) {
          const evidenceLink = evidenceLinkElement.href;
          plan.evidenceOfCoverageLink = evidenceLink.startsWith('http') ? evidenceLink : `https://wellcare.isf.io${evidenceLink}`;
        } else {
          plan.evidenceOfCoverageLink = null;
        }
      } catch (detailError) {
        plan.evidenceOfCoverageLink = null;
      }
    }

    return planData;

  } catch (error) {
    console.error(`Error fetching plan data for Zip Code: ${zipCode}`, error);
    return [];
  }
}

// Function to save data to Firebase
async function saveToFirebase(plans) {
  const maxRetries = 5;

  const commitBatch = async (batch) => {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        await batch.commit();
        break;
      } catch (e) {
        console.log(`Resource exhausted, retrying... ${e}`);
        await new Promise(res => setTimeout(res, 2 ** attempt * 1000)); // Exponential backoff
      }
    }
  };

  const batchSize = 10;

  // Save plans
  const plansCollection = db.collection('plans');
  for (let i = 0; i < plans.length; i += batchSize) {
    const batch = db.batch();
    const planChunk = plans.slice(i, i + batchSize);
    planChunk.forEach(plan => {
      const planRef = plansCollection.doc(`${plan.productContractCode}-${plan.zipCode}`);
      const planData = { ...plan };
      if (planData.rating === 0) {
        planData.rating = null;
      }
      batch.set(planRef, planData);
    });
    await commitBatch(batch);
    console.log(`Saved ${planChunk.length} plans to Firebase.`);
  }
}

async function main() {
  try {
    const zipMapping = JSON.parse(await fs.readFile('./final_zip_mapping.json', 'utf-8'));
    let allPlans = new Map();

    const token = await fetchRequestVerificationToken();
    const sortedZipCodes = Object.keys(zipMapping).sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));

    for (const zipCode of sortedZipCodes) {
      console.log(`Checking ZIP code: ${zipCode}`);

      const { county_name, state_abbreviation, fips_codes } = zipMapping[zipCode];

      for (const fipsCode of fips_codes) {
        const plans = await getPlanData(zipCode, county_name, state_abbreviation, fipsCode, token);

        if (plans.length > 0) {
          plans.forEach(plan => {
            allPlans.set(`${plan.productContractCode}-${plan.zipCode}`, plan);
          });
        }

        if (allPlans.size >= 100) {
          await saveToFirebase(Array.from(allPlans.values()));
          allPlans.clear();
        }
      }
    }

    if (allPlans.size > 0) {
      await saveToFirebase(Array.from(allPlans.values()));
    }

    console.log('Plan information has been saved to Firebase');
  } catch (error) {
    console.error('Error:', error);
  }
}

// Run the main function
main();
