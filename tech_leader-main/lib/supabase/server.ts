export async function getUserFromBearer(_req: Request) {
  return { user: { id: "mock-user" }, error: null };
}

export function getSupabaseServiceClient() {
  const chain = {
    select: (_columns?: string) => chain,
    order: (_column: string, _options?: { ascending?: boolean }) => chain,
    limit: (_count: number) => Promise.resolve({ data: [] as unknown[], error: null as { message: string } | null }),
  };

  return {
    from: (_table: string) => ({
      insert: async (_payload: Record<string, unknown>) => ({ error: null as { message: string } | null }),
      select: (_columns?: string) => chain,
      order: (_column: string, _options?: { ascending?: boolean }) => chain,
      limit: (_count: number) => Promise.resolve({ data: [] as unknown[], error: null as { message: string } | null }),
    }),
  };
}
