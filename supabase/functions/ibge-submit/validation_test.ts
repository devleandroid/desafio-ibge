import { assertEquals } from "jsr:@std/assert";
import { parseStatistics } from "./validation.ts";

Deno.test("accepts a valid statistics payload", () => {
  assertEquals(
    parseStatistics({
      total_municipios: 3,
      total_ok: 1,
      total_nao_encontrado: 1,
      total_ambiguo: 1,
      total_erro_api: 0,
      pop_total_ok: 500,
      medias_por_regiao: { Sul: 500 },
    }),
    {
      total_municipios: 3,
      total_ok: 1,
      total_nao_encontrado: 1,
      total_ambiguo: 1,
      total_erro_api: 0,
      pop_total_ok: 500,
      medias_por_regiao: { Sul: 500 },
    },
  );
});

Deno.test("rejects status totals that do not match the batch total", () => {
  assertEquals(
    parseStatistics({
      total_municipios: 3,
      total_ok: 1,
      total_nao_encontrado: 1,
      total_ambiguo: 0,
      total_erro_api: 0,
      pop_total_ok: 500,
      medias_por_regiao: {},
    }),
    null,
  );
});

Deno.test("rejects invalid counts, populations, and regional averages", () => {
  const validPayload = {
    total_municipios: 1,
    total_ok: 1,
    total_nao_encontrado: 0,
    total_ambiguo: 0,
    total_erro_api: 0,
    pop_total_ok: 500,
    medias_por_regiao: { Sul: 500 },
  };

  assertEquals(parseStatistics({ ...validPayload, total_ok: -1 }), null);
  assertEquals(parseStatistics({ ...validPayload, pop_total_ok: 1.5 }), null);
  assertEquals(
    parseStatistics({ ...validPayload, medias_por_regiao: { Sul: Infinity } }),
    null,
  );
});
