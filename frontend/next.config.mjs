/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow cross-origin requests from the preview domain
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
};

export default nextConfig;