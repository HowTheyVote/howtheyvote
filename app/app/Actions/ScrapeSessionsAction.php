<?php

namespace App\Actions;

use App\Enums\LocationEnum;
use App\Session;

class ScrapeSessionsAction extends Action
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction)
    {
        $this->scrapeAction = $scrapeAction;
    }

    public function execute(int $year, int $month): void
    {
        $data = $this->scrapeAction->execute('sessions', [
            'year' => $year,
            'month' => $month,
        ]);

        foreach ($data as $session) {
            Session::updateOrCreate([
                'start_date' => $session['start_date'],
                'end_date' => $session['end_date'],
                ],
            ['location' => LocationEnum::make($session['location']),
            ]);
        }
    }
}
