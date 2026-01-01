import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Still',
  description: 'A moment of reflection.',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false, // Intentional restriction for app-like feel
};

import { Providers } from './providers';

// export default function RootLayout({
//   children,
// }: {
//   children: React.ReactNode;
// }) {
//   return (
//     <html lang="en">
//       <body className="antialiased min-h-screen flex flex-col items-center justify-center overflow-hidden selection:bg-gray-800 selection:text-white">
//   <Providers>
//     <main className="w-full max-w-md px-8 py-12 flex flex-col min-h-screen relative">
//       {children}
//     </main>
//   </Providers>
// </body>
//     </html>
//   );
// }

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen flex flex-col items-center justify-center selection:bg-gray-800 selection:text-white">
        <main className="w-full max-w-md px-8 py-12 flex flex-col min-h-screen relative">
          <Providers>
            {children}
          </Providers>
        </main>
      </body>
    </html>
  );
}
