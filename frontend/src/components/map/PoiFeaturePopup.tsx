'use client';

import type { GeoPointFeature } from '@/types/api';

type PoiFeaturePopupProps = {
  feature: GeoPointFeature;
};

function renderMeta(label: string, value?: string | number | null) {
  if (value === undefined || value === null || value === '') {
    return null;
  }

  return (
    <div className="grid grid-cols-[72px_minmax(0,1fr)] gap-2 text-xs text-muted-foreground">
      <span className="font-medium text-foreground/80">{label}</span>
      <span className="break-words">{value}</span>
    </div>
  );
}

export function PoiFeaturePopup({ feature }: PoiFeaturePopupProps) {
  const { properties } = feature;
  const isPharmacy = properties.layer === 'pharmacies';
  const title = properties.display_name ?? properties.name;
  const addressLines = [properties.address_line_1, properties.address_line_2].filter(
    (line): line is string => Boolean(line)
  );
  const cityLine = [properties.postal_code, properties.city].filter(Boolean).join(' ');

  return (
    <div className="min-w-[220px] space-y-3 text-sm">
      <div className="space-y-1">
        <div className="text-[11px] font-semibold uppercase tracking-[0.2em]" style={{ color: properties.layer_color ?? '#334155' }}>
          {properties.layer_label ?? properties.layer.replaceAll('_', ' ')}
        </div>
        <div className="font-semibold text-foreground">{title}</div>
        {addressLines.map((line) => (
          <div key={line} className="text-muted-foreground">
            {line}
          </div>
        ))}
        {cityLine ? <div className="text-muted-foreground">{cityLine}</div> : null}
        {properties.opening_hours ? <div className="text-xs text-muted-foreground">Horaires: {properties.opening_hours}</div> : null}
      </div>

      <div className="space-y-1.5 border-t pt-3">
        {isPharmacy ? (
          <div className="space-y-1 rounded-md bg-accent/30 p-2">
            <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-foreground/80">Pharmaciens</div>
            <div className="text-sm text-foreground">
              Total : <span className="font-semibold">{properties.pharmacist_count ?? 0}</span>
            </div>
            {properties.pharmacy_type ? <div className="text-xs text-muted-foreground">Type : {properties.pharmacy_type}</div> : null}
          </div>
        ) : null}
        {renderMeta('Telephone', properties.phone)}
        {properties.website ? (
          <div className="grid grid-cols-[72px_minmax(0,1fr)] gap-2 text-xs text-muted-foreground">
            <span className="font-medium text-foreground/80">Site</span>
            <a className="break-all text-primary underline-offset-2 hover:underline" href={properties.website} target="_blank" rel="noreferrer">
              {properties.website}
            </a>
          </div>
        ) : null}
        {renderMeta('FINESS', properties.finess)}
        {renderMeta('RPPS', properties.rpps)}
        {renderMeta('ADELI', properties.adeli)}
        {renderMeta('SIRET', properties.siret)}
        {!isPharmacy ? renderMeta('Source', properties.source_name) : null}
        {!isPharmacy ? renderMeta('Geocodage', properties.geocode_status) : null}
      </div>
    </div>
  );
}
