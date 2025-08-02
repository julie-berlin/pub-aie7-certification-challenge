# IntegriBot Frontend

A Next.js frontend for the IntegriBot federal ethics compliance assistant.

## Features

- **User Context Collection**: Captures user role, agency, seniority, and clearance level
- **Chat Interface**: Interactive conversation with the ethics AI assistant
- **Real-time Responses**: Streams responses from the backend API
- **Responsive Design**: Works on desktop and mobile devices
- **TypeScript**: Full type safety throughout the application

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Native fetch API

## Getting Started

### Prerequisites

- Node.js 22.x or higher
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env.local
```

3. Update the API URL in `.env.local` if needed:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler

### Project Structure

```
src/
├── app/                 # Next.js app directory
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Home page
├── components/         # React components
│   ├── ChatInterface.tsx
│   ├── ChatMessage.tsx
│   └── UserContextForm.tsx
├── lib/               # Utility functions
│   ├── api.ts         # API client
│   └── utils.ts       # Helper functions
└── types/             # TypeScript type definitions
    └── index.ts
```

## API Integration

The frontend communicates with the FastAPI backend through:

- `POST /api/assess` - Submit ethics questions for assessment
- `GET /api/health` - Health check endpoint

## Deployment

### Production Build

```bash
npm run build
npm run start
```

### Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NODE_ENV` - Environment (development/production)

## Contributing

1. Follow the existing code style and conventions
2. Use TypeScript for all new code
3. Add proper error handling for API calls
4. Test responsive design on multiple screen sizes