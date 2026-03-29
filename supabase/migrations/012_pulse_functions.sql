-- Anonymous aggregated stats for community pulse (no PII exposed)
CREATE OR REPLACE FUNCTION get_pulse_stats()
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'total_analyses', (SELECT COUNT(*) FROM analyses),
    'total_users', (SELECT COUNT(*) FROM profiles),
    'total_people', (SELECT COUNT(*) FROM people),
    'avg_toxicity_score', (
      SELECT COALESCE(ROUND(AVG(toxicity_score)::numeric, 1), 0) FROM analyses
    ),
    'high_risk_percentage', (
      SELECT COALESCE(
        ROUND((COUNT(*) FILTER (WHERE risk_level = 'high')::numeric / NULLIF(COUNT(*), 0) * 100)::numeric, 0),
        0
      )
      FROM analyses
    ),
    'top_traits', (
      SELECT COALESCE(json_agg(t.trait_name ORDER BY t.cnt DESC), '[]'::json)
      FROM (
        SELECT elem->>'name' AS trait_name, COUNT(*) AS cnt
        FROM analyses, jsonb_array_elements(detected_traits) AS elem
        GROUP BY elem->>'name'
        ORDER BY cnt DESC
        LIMIT 10
      ) t
    ),
    'analyses_this_week', (
      SELECT COUNT(*) FROM analyses
      WHERE created_at > NOW() - INTERVAL '7 days'
    ),
    'avg_score_this_week', (
      SELECT COALESCE(ROUND(AVG(toxicity_score)::numeric, 1), 0) FROM analyses
      WHERE created_at > NOW() - INTERVAL '7 days'
    ),
    'top_threat_types', (
      SELECT COALESCE(json_agg(t.threat_type ORDER BY t.cnt DESC), '[]'::json)
      FROM (
        SELECT threat_type, COUNT(*) AS cnt
        FROM analyses
        WHERE threat_type IS NOT NULL
        GROUP BY threat_type
        ORDER BY cnt DESC
        LIMIT 5
      ) t
    )
  ) INTO result;

  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
