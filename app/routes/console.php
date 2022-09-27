<?php

use App\Actions\CreateMemberImageAction;
use App\Actions\GenerateVoteSharePicAction;
use App\Actions\MatchVotesAndVotingListsAction;
use App\Actions\ScrapeMemberGroupsAction;
use App\Actions\ScrapeMemberInfoAction;
use App\Actions\ScrapeMembersAction;
use App\Actions\ScrapeSessionsAction;
use App\Actions\ScrapeVoteCollectionsAction;
use App\Actions\ScrapeVotingListsAction;
use App\Member;
use App\Session;
use App\Term;
use App\VoteCollection;
use App\VotingList;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\Artisan;

/*
|--------------------------------------------------------------------------
| Console Routes
|--------------------------------------------------------------------------
|
| This file is where you may define all of your Closure based console
| commands. Each Closure is bound to a command instance allowing a
| simple approach to interacting with each command's IO methods.
|
*/

Artisan::command('scrape:members {--term=}', function (
    int $term,
    ScrapeMembersAction $action
) {
    $term = Term::whereNumber($term)->first();
    $this->info("Scraping list of members for term {$term->number}.");

    $action->execute($term);
})->describe('Scrape and save all members (without info) for a given term.');

Artisan::command('scrape:members-info {--term=}', function (
    int $term,
    ScrapeMemberInfoAction $action
) {
    $term = Term::whereNumber($term)->first();
    $members = $term->members()->get();

    $this->info("Scraping info for all members in term {$term->number}.");
    $this->withProgressBar($members, fn ($member) => $action->execute($member));
})->describe('Scrape and save info for all saved members.');

Artisan::command('scrape:members-photos {--all}', function (
    bool $all,
    CreateMemberImageAction $action
) {
    $members = $all ? Member::all() : Member::all()->filter(function ($member) {
        return ! $member->hasProfilePicture();
    });

    $this->info('Scraping profile photos for members.');
    $this->withProgressBar($members, fn ($member) => $action->execute($member));
});

Artisan::command('scrape:members-groups {--term=}', function (
    int $term,
    ScrapeMemberGroupsAction $action
) {
    $term = Term::whereNumber($term)->first();
    $members = $term->members()->get();

    $this->info("Scraping group memberships for all members in term {$term->number}");
    $this->withProgressBar($members, fn ($member) => $action->execute($member, $term));
})->describe('Scrape and save group info for all saved members for the given term.');

Artisan::command('scrape:sessions {--term=} {--year=} {--month=}', function (
    int $term,
    int $month,
    int $year,
    ScrapeSessionsAction $action
) {
    $action->execute($term, $year, $month);
});

Artisan::command('scrape:voting-lists {--term=} {--date=}', function (
    int $term,
    string $date,
    ScrapeVotingListsAction $action
) {
    $term = Term::whereNumber($term)->first();
    $date = Carbon::parse($date);

    $this->info("Scraping voting lists for {$date}");
    $action->execute($term, $date);
})->describe('Scrape and save all voting lists with compiled stats for the given date and term.');

Artisan::command('scrape:vote-collections {--term=} {--date=}', function (
    int $term,
    string $date,
    ScrapeVoteCollectionsAction $action
) {
    $term = Term::whereNumber($term)->first();
    $date = Carbon::parse($date);

    $this->info("Scraping vote collections for {$date}");
    $action->execute($term, $date);
})->describe('Scrape and save all vote collections for the given date and term.');

Artisan::command('scrape:all {--term=}', function (int $term) {
    Artisan::call('scrape:members', ['--term' => $term]);
    Artisan::call('scrape:members-groups', ['--term' => $term]);
    Artisan::call('scrape:members-info', ['--term' => $term]);
    Artisan::call('scrape:members-photos');
    Artisan::call('scrape:sessions', [
        '--term' => $term,
        '--month' => Carbon::now()->month,
        '--year' => Carbon::now()->year,
    ]);

    // Get the newest session without associated votes and try to
    // scrape voting lists and votes for the days of the session.
    $session = Session::query()
        ->whereDoesntHave('votes')
        ->whereNull('ignore_when_scraping_voting_lists')
        ->orderBy('start_date', 'desc')
        ->first();

    if (! $session) {
        return $this->info('Exiting as all sessions already have associated votes.');
    }

    $period = $session->start_date->toPeriod($session->end_date);

    $count = VoteCollection::count();

    foreach ($period as $date) {
        Artisan::call('scrape:vote-collections', [
            '--term' => $term,
            '--date' => $date,
        ]);

        // Vote collection documents on the Parliament's website
        // include all vote collections for the session, including
        // vote collections that did not take place on the given
        // day, i.e. we have to make sure to import vote collections
        // only for the first day of the plenary session.
        // It is necessary to loop over all days, since the actual first day where
        // the collections are available is not always the first day of the session.
        if (VoteCollection::count() > $count) {
            break;
        }
    }

    foreach ($period as $date) {
        Artisan::call('scrape:voting-lists', [
            '--term' => $term,
            '--date' => $date,
        ]);
    }

    Artisan::call('scrape:match');
})->describe('Runs all scrapers for the given date and matches votes and voting lists.');

Artisan::command('scrape:match', function (MatchVotesAndVotingListsAction $action) {
    $action->execute();
})->describe('Matches all available votes to their voting lists.');

Artisan::command('share-picture:vote {--votingList=}', function (
    int $votingList,
    GenerateVoteSharePicAction $action
) {
    $votingList = VotingList::find($votingList);
    $action->execute($votingList);
})->describe('Generates a picture showing the overall result for a given vote.');
