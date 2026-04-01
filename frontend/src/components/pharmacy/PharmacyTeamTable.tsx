import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { PharmacistDetailResponse } from '@/types/api';

type PharmacyTeamTableProps = {
  pharmacists: PharmacistDetailResponse[];
};

export function PharmacyTeamTable({ pharmacists }: PharmacyTeamTableProps) {
  return (
    <Card>
      <CardHeader className='px-4 py-3'>
        <CardTitle className='text-base'>Équipe officinale</CardTitle>
      </CardHeader>
      <CardContent className='px-4 pb-4'>
        <div className='overflow-x-auto'>
          <table className='min-w-full text-sm'>
            <thead>
              <tr className='border-b text-left text-muted-foreground'>
                <th className='px-2 py-2 font-medium'>Nom</th>
                <th className='px-2 py-2 font-medium'>Prénom</th>
                <th className='px-2 py-2 font-medium'>RPPS</th>
                <th className='px-2 py-2 font-medium'>Diplôme principal</th>
                <th className='px-2 py-2 font-medium'>Première inscription</th>
                <th className='px-2 py-2 font-medium'>Fonction</th>
                <th className='px-2 py-2 font-medium'>Activité principale</th>
              </tr>
            </thead>
            <tbody>
              {pharmacists.map((pharmacist) => {
                const primaryActivity = pharmacist.activities.find((activity) => activity.is_primary_activity) ?? pharmacist.activities[0];
                const primaryDegree = pharmacist.degrees[0];

                return (
                  <tr key={pharmacist.rpps} className='border-b last:border-b-0'>
                    <td className='px-2 py-2'>{pharmacist.last_name || '/'}</td>
                    <td className='px-2 py-2'>{pharmacist.first_name || '/'}</td>
                    <td className='px-2 py-2'>{pharmacist.rpps}</td>
                    <td className='px-2 py-2'>{primaryDegree?.degree_label || '/'}</td>
                    <td className='px-2 py-2'>{pharmacist.first_registration_date || '/'}</td>
                    <td className='px-2 py-2'>{primaryActivity?.function_label || '/'}</td>
                    <td className='px-2 py-2'>{primaryActivity?.is_primary_activity ? 'Oui' : 'Non'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
