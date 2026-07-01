# syntax=docker/dockerfile:1
# Build context must be the monorepo root:
#   docker build -f apps/web/Dockerfile -t drawly-web .

FROM node:22-alpine AS base
RUN corepack enable
WORKDIR /app

# ---- Prune the workspace down to what @drawly/web actually needs ----
FROM base AS pruner
RUN npm install --global turbo@2.5.6
COPY . .
RUN turbo prune @drawly/web --docker

# ---- Install dependencies for the pruned workspace ----
FROM base AS installer
COPY --from=pruner /app/out/json/ .
RUN pnpm install --frozen-lockfile

# ---- Development image: source is bind-mounted by docker-compose ----
FROM installer AS dev
COPY --from=pruner /app/out/full/ .
EXPOSE 3000
CMD ["pnpm", "--filter", "@drawly/web", "dev"]

# ---- Production build ----
FROM installer AS builder
COPY --from=pruner /app/out/full/ .
RUN pnpm turbo run build --filter=@drawly/web

# ---- Production runtime ----
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /app/apps/web/public ./apps/web/public
USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["node", "apps/web/server.js"]
