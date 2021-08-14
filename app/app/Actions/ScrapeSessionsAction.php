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

    public function execute(int $year, int $month): void
    {
        try {
            $data = $this->scrapeAction->execute('sessions', [
                'year' => $year,
                'month' => $month,
            ]);
        } catch (ScrapingException $exception) {
            report($exception);

            return;
        }

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
