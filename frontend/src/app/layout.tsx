import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'IntegriBot - Federal Ethics Compliance Assistant',
  description: 'AI-powered federal ethics compliance guidance and violation assessment',
  keywords: ['federal ethics', 'compliance', 'government', 'ethics violations', 'OGE'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-federal-light">
          {children}
        </div>
      </body>
    </html>
  )
}