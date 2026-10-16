export interface MunicipalityStatistics {
  total_municipios: number;
  total_ok: number;
  total_nao_encontrado: number;
  total_ambiguo: number;
  total_erro_api: number;
  pop_total_ok: number;
  medias_por_regiao: Record<string, number>;
}

/** Validates the JSON payload before it is persisted to PostgreSQL. */
export function parseStatistics(value: unknown): MunicipalityStatistics | null {
  if (!isRecord(value) || !isRecord(value.medias_por_regiao)) {
    return null;
  }
  if (
    !isNonNegativeInteger(value.total_municipios) ||
    value.total_municipios > 2_147_483_647 ||
    !isNonNegativeInteger(value.total_ok) ||
    value.total_ok > 2_147_483_647 ||
    !isNonNegativeInteger(value.total_nao_encontrado) ||
    value.total_nao_encontrado > 2_147_483_647 ||
    !isNonNegativeInteger(value.total_ambiguo) ||
    value.total_ambiguo > 2_147_483_647 ||
    !isNonNegativeInteger(value.total_erro_api) ||
    value.total_erro_api > 2_147_483_647 ||
    !isNonNegativeInteger(value.pop_total_ok)
  ) {
    return null;
  }
  if (
    value.total_municipios !==
      value.total_ok + value.total_nao_encontrado + value.total_ambiguo +
        value.total_erro_api
  ) {
    return null;
  }

  const regionalAverages: Record<string, number> = {};
  for (const [region, average] of Object.entries(value.medias_por_regiao)) {
    if (typeof average !== "number" || !Number.isFinite(average) || average < 0) {
      return null;
    }
    regionalAverages[region] = average;
  }

  return {
    total_municipios: value.total_municipios,
    total_ok: value.total_ok,
    total_nao_encontrado: value.total_nao_encontrado,
    total_ambiguo: value.total_ambiguo,
    total_erro_api: value.total_erro_api,
    pop_total_ok: value.pop_total_ok,
    medias_por_regiao: regionalAverages,
  };
}

/** Narrows JSON objects without accepting null or arrays as records. */
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Accepts only safe, non-negative integers from the JSON payload. */
function isNonNegativeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isSafeInteger(value) && value >= 0;
}
