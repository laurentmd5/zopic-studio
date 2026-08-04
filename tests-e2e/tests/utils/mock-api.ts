import { Page } from '@playwright/test';

export const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': '*'
};

export class MockBackend {
  page: Page;
  
  // State
  currentUser: any = null;
  competitions: any[] = [];
  photos: any[] = [];
  purchases: any[] = [];
  favorites: any[] = [];

  constructor(page: Page) {
    this.page = page;
  }

  async setup() {
    await this.page.route('http://localhost:8000/api/v1/**', async (route, request) => {
      const url = request.url();
      const method = request.method();
      
      console.log(`[MOCK] ${method} ${url}`);

      if (method === 'OPTIONS') {
        return route.fulfill({ status: 200, headers: corsHeaders });
      }

      // ----------------------------------------------------
      // ATHLETES
      // ----------------------------------------------------
      if (url.includes('/athletes/me/timeline') && method === 'GET') {
        const mockTimeline = {
          timeline: [
            {
              year: 2026,
              competitions: [
                {
                  id: "1",
                  name: "Finale Navétanes Pikine",
                  date: "2026-08-15T10:00:00Z",
                  sport: "football",
                  location: "Stade Alassane Djigo, Pikine",
                  photos_count: 12,
                  cover_photo_url: "https://placehold.co/300x200/png?text=Navetanes"
                },
                {
                  id: "2",
                  name: "Marathon Dakar",
                  date: "2026-07-22T08:00:00Z",
                  sport: "athletisme",
                  location: "Corniche Ouest, Dakar",
                  photos_count: 8,
                  cover_photo_url: "https://placehold.co/300x200/png?text=Marathon"
                }
              ]
            }
          ],
          total_competitions: 2,
          total_photos: 20,
          message: "Le début d'une grande aventure 🚀"
        };
        return route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(mockTimeline) });
      }

      // ----------------------------------------------------
      // AUTH
      // ----------------------------------------------------
      if (url.includes('/auth/otp/send') && method === 'POST') {
        return route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify({ message: "OTP sent" }) });
      }

      if (url.includes('/auth/otp/verify') && method === 'POST') {
        const payload = request.postDataJSON();
        if (payload.otp === '123456') {
          this.currentUser = {
            id: 1,
            phone_number: payload.phone_number,
            full_name: "Photographe Test",
            role: "photographer",
            studio_name: "Test Studio",
            city: "Dakar"
          };
          return route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify({ access_token: "mock_token", token_type: "bearer" }) });
        }
        return route.fulfill({ status: 400, headers: corsHeaders, body: JSON.stringify({ detail: "OTP invalide" }) });
      }

      if (url.includes('/auth/me') && method === 'GET') {
        if (this.currentUser) {
          return route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(this.currentUser) });
        }
        return route.fulfill({ status: 401, headers: corsHeaders, body: JSON.stringify({ detail: "Not authenticated" }) });
      }

      // ----------------------------------------------------
      // SUBSCRIPTIONS
      // ----------------------------------------------------
      if (url.includes('/subscriptions/plans') && method === 'GET') {
        return route.fulfill({
          status: 200, headers: corsHeaders, body: JSON.stringify([
            { id: 1, name: "Starter", monthly_price: 5000, max_storage_gb: 10, commission_rate: 12 },
            { id: 2, name: "Pro", monthly_price: 15000, max_storage_gb: 50, commission_rate: 8 }
          ])
        });
      }

      if (url.includes('/subscriptions/me') && method === 'GET') {
        return route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(null) }); // No active subscription by default
      }

      if (url.includes('/subscriptions/storage') && method === 'GET') {
        return route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify({ used_bytes: 0, total_bytes: 10 * 1024 * 1024 * 1024 }) });
      }

      // ----------------------------------------------------
      // COMPETITIONS
      // ----------------------------------------------------
      if (url.match(/\/competitions\/?$/) && method === 'GET') {
        return route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(this.competitions) });
      }

      if (url.includes('/competitions') && method === 'POST') {
        const payload = request.postDataJSON();
        const newComp = {
          id: Math.floor(Math.random() * 1000) + 1,
          name: payload.name,
          date: payload.date,
          location: payload.location,
          status: 'Brouillon',
          settings: { price_per_photo: 1500, pack_3_price: 4000, pack_5_price: 6000, all_photos_price: 10000 },
          photos_count: 0
        };
        this.competitions.push(newComp);
        return route.fulfill({ status: 201, headers: corsHeaders, body: JSON.stringify(newComp) });
      }

      if (url.match(/\/competitions\/\d+$/) && method === 'GET') {
        const id = parseInt(url.split('/').pop() || '0');
        const comp = this.competitions.find(c => c.id === id) || {
          id, name: 'Marathon E2E', date: new Date().toISOString(), status: 'Publié',
          settings: { price_per_photo: 1500, pack_3_price: 4000, pack_all_price: 10000 }, photos_count: 3
        };
        return route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(comp) });
      }

      // ----------------------------------------------------
      // SEARCH & PHOTOS
      // ----------------------------------------------------
      if (url.includes('/search/competitions') && method === 'GET') {
        return route.fulfill({
          status: 200, headers: corsHeaders, body: JSON.stringify({
            results: this.photos.length > 0 ? this.photos : [
              { id: 101, url: 'mock1.jpg', watermark_url: 'mock1.jpg', price: 1500 },
              { id: 102, url: 'mock2.jpg', watermark_url: 'mock2.jpg', price: 1500 },
              { id: 103, url: 'mock3.jpg', watermark_url: 'mock3.jpg', price: 1500 }
            ]
          })
        });
      }

      // ----------------------------------------------------
      // PAYMENTS & PURCHASES
      // ----------------------------------------------------
      if (url.includes('/payments/init') && method === 'POST') {
        return route.fulfill({
          status: 200, headers: corsHeaders, body: JSON.stringify({
            payment_url: 'http://localhost:5174/downloads?success=true',
            transaction_id: 'txn_mock'
          })
        });
      }

      if (url.includes('/payments/purchases') && method === 'GET') {
        return route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(this.purchases) });
      }

      // ----------------------------------------------------
      // FAVORITES
      // ----------------------------------------------------
      if (url.includes('/favorites') && method === 'GET') {
        return route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(this.favorites) });
      }
      
      if (url.includes('/favorites') && method === 'POST') {
        const payload = request.postDataJSON();
        this.favorites.push({ photo_id: payload.photo_id });
        return route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify({ success: true }) });
      }
      
      if (url.includes('/favorites/') && method === 'DELETE') {
        const photoId = parseInt(url.split('/').pop() || '0');
        this.favorites = this.favorites.filter(f => f.photo_id !== photoId);
        return route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify({ success: true }) });
      }

      // Fallback
      return route.continue();
    });
  }
}
