<?php

namespace App\Actions;

use App\Enums\LocationEnum;
use App\Exceptions\ScrapingException;
use App\Session;

class ScrapeSessionsAction extends Action
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction)
    {
        $this->scrapeAction = $scrapeAction;
    }

    public function execute(int $term, int $year, int $month): void
    {
        try {
            $parlData = $this->scrapeAction->execute('sessions_parl', [
                'term' => $term,
                'year' => $year,
                'month' => $month,
            ]);

            $obsData = $this->scrapeAction->execute('sessions_obs', [
                'year' => $year,
                'month' => $month,
            ]);
        } catch (ScrapingException $exception) {
            report($exception);

            return;
        }

        foreach ($parlData as $session) {
            Session::updateOrCreate([
                'start_date' => $session['start_date'],
                'end_date' => $session['end_date'],
            ],
            ['location' => LocationEnum::NONE(),
            ]);
        }

        foreach ($obsData as $session) {
            Session::updateOrCreate([
                'start_date' => $session['start_date'],
                'end_date' => $session['end_date'],
            ],
            ['location' => LocationEnum::make($session['location']),
            ]);
        }
    }
}
