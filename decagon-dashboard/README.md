# Signal

A real-time sales pipeline dashboard for tracking target prospects, built with Convex and React. ICPs (Ideal Customer Profiles) represent the customer segments we want to win. Sierra is a competitor.

## Features

- **Companies View**: Track target companies by ICP, priority, and status
- **Contacts View**: Browse decision makers and key contacts
- **Outreach View**: Monitor email/LinkedIn outreach and response rates
- **Real-time Updates**: Changes sync instantly across all clients

## Setup

### 1. Install Dependencies

```bash
cd decagon-dashboard
npm install
```

### 2. Create Convex Account & Project

1. Go to [https://dashboard.convex.dev](https://dashboard.convex.dev)
2. Sign up / Log in with GitHub
3. When you run `npx convex dev`, it will prompt you to create a new project

### 3. Start Convex Development Server

```bash
npx convex dev
```

This will:
- Prompt you to log in to Convex (first time)
- Create a new project or link to existing
- Deploy your schema and functions
- Output your deployment URL

### 4. Set Environment Variable

Copy the deployment URL and create `.env.local`:

```bash
echo "VITE_CONVEX_URL=https://your-deployment.convex.cloud" > .env.local
```

Or copy from `.env.example` and fill in your URL.

### 5. Migrate Data

Import your existing Decagon data:

```bash
# Make sure CONVEX_URL is set (use the same URL as VITE_CONVEX_URL)
export CONVEX_URL=https://your-deployment.convex.cloud
npm run migrate
```

### 6. Start Development Server

In a new terminal (keep `npx convex dev` running):

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
decagon-dashboard/
├── convex/                 # Convex backend
│   ├── schema.ts          # Database schema
│   ├── companies.ts       # Company queries/mutations
│   ├── contacts.ts        # Contact queries/mutations
│   ├── outreach.ts        # Outreach tracking
│   └── signals.ts         # Company signals
├── src/                    # React frontend
│   ├── App.tsx            # Main dashboard component
│   ├── main.tsx           # Entry point
│   └── index.css          # Styles
├── scripts/
│   └── migrate-data.ts    # Data migration script
└── package.json
```

## Schema

### Companies
- `name`, `domain`, `icp`, `priority`, `signalStrength`
- `whyFit`, `decisionMakerTitles`, `status`, `owner`, `notes`

### Contacts
- `companyId`, `name`, `title`, `jobFunction`, `jobLevel`
- `linkedinUrl`, `email`, `personaScore`, `outreachStatus`

### Outreach
- `contactId`, `companyId`, `channel`, `messageType`
- `subject`, `messageContent`, `sentAt`, `response`

### Signals
- `companyId`, `signalType`, `title`, `description`
- `sourceUrl`, `discoveredAt`, `relevanceScore`

## Deployment

Deploy to production:

```bash
npx convex deploy
```

The frontend can be deployed to Vercel, Netlify, etc.

## API Usage

You can also use the Convex client directly from your Python scripts:

```python
# pip install convex
from convex import ConvexClient

client = ConvexClient("https://your-deployment.convex.cloud")

# Query companies
companies = client.query("companies:list")

# Update company status
client.mutation("companies:updateStatus", {
    "id": company_id,
    "status": "Contacted"
})
```
