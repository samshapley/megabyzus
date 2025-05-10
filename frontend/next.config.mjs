/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow cross-origin requests from the preview domain and API service
  async headers() {
    return [
      {
        // Apply these headers to all routes
        source: '/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
        ],
      },
    ]
  },
  
  // Allow development origins for the preview environment (for future Next.js versions)
  allowedDevOrigins: [
    'b75ipyserir7koxg.preview.dev.igent.ai',
    '*.preview.dev.igent.ai',
  ],

  // Define runtime environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  },

  // Add rewrites for the API to avoid CORS issues during development
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        // Use localhost directly since we're in the same container
        destination: 'http://localhost:8080/api/:path*',
      },
    ]
  },
};

export default nextConfig;
