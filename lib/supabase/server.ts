type SupabaseError = { message: string };

type SupabaseQueryResult<T> = {
  data: T | null;
  error: SupabaseError | null;
};

type SupabaseSelectBuilder<Row> = {
  order(column: string, options?: { ascending?: boolean }): SupabaseSelectBuilder<Row>;
  limit(count: number): Promise<SupabaseQueryResult<Row[]>>;
};

type SupabaseTableBuilder<Row> = {
  insert(payload: Record<string, unknown>): Promise<SupabaseQueryResult<null>>;
  select(columns?: string): SupabaseSelectBuilder<Row>;
};

type SupabaseClient = {
  from<Row = Record<string, unknown>>(table: string): SupabaseTableBuilder<Row>;
};

function createSelectBuilder<Row>(): SupabaseSelectBuilder<Row> {
  return {
    order() {
      return this;
    },
    async limit() {
      return { data: [], error: null };
    },
  };
}

function createSupabaseClient(): SupabaseClient {
  return {
    from<Row>() {
      return {
        async insert() {
          return { data: null, error: null };
        },
        select() {
          return createSelectBuilder<Row>();
        },
      };
    },
  };
}

export function getSupabaseServiceClient(): SupabaseClient {
  return createSupabaseClient();
}

export async function getUserFromBearer(req: Request): Promise<{ user: { id: string } | null; error: string | null }> {
  void req;
  return { user: null, error: "Unauthorized" };
}
