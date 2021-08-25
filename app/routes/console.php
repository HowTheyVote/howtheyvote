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
    $this->info("Scraping list of members for term {$term}");

    $action->execute($term);
})->describe('Scrape and save all members (without info) for a given term.');

Artisan::command('scrape:members-info {--term=}', function (
    int $term,
    ScrapeMemberInfoAction $action
) {
    $allMembersInTerm = Term::where('number', $term)->first()->members()->get();
    $membersCount = $allMembersInTerm->count();

    foreach ($allMembersInTerm as $index => $member) {
        $progress = ($index + 1).'/'.$membersCount;
        $this->output->write("\r<info>Scraping info for member: {$progress}</info>");

        $action->execute($member);
    }

    $this->output->writeln('');
})->describe('Scrape and save info for all saved members.');

Artisan::command('scrape:members-photos', function (CreateMemberImageAction $action) {
    $allMembers = Member::all();
    $membersCount = $allMembers->count();

    foreach ($allMembers as $index => $member) {
        $progress = ($index + 1).'/'.$membersCount;
        $this->output->write("\r<info>Creating thumbnail for member: {$progress}</info>");

        $action->execute($member);
    }

    $this->output->writeln('');
});

Artisan::command('scrape:members-groups {--term=}', function (
    int $term,
    ScrapeMemberGroupsAction $action
) {
    $term = Term::whereNumber($term)->first();
    $allMembersInTerm = $term->members()->get();

    $membersCount = $allMembersInTerm->count();

    foreach ($allMembersInTerm as $index => $member) {
        $progress = ($index + 1).'/'.$membersCount;
        $this->output->write("\r<info>Scraping groups for member {$progress}</info>");

        $action->execute($member, $term);
    }

    $this->output->writeln('');
})->describe('Scrape and save group info for all saved members for the given term.');

Artisan::command('scrape:sessions {--year=} {--month=}', function (
    int $month,
    int $year,
    ScrapeSessionsAction $action
) {
    $action->execute($year, $month);
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

    $this->output->writeln('');
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

    $this->output->writeln('');
})->describe('Scrape and save all vote collections for the given date and term.');

Artisan::command('scrape:all {--term=} {--from=} {--to=}', function (
    int $term,
    string $from,
    string $to
) {
    $period = Carbon::parse($from)->toPeriod($to);

    Artisan::call('scrape:members', ['--term' => $term]);
    Artisan::call('scrape:members-groups', ['--term' => $term]);
    Artisan::call('scrape:members-info', ['--term' => $term]);

    $from = Carbon::parse($from);
    $month = $from->month;
    $year = $from->year;
    Artisan::call('scrape:sessions', [
        '--year' => $year,
        '--month' => $month,
    ]);

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
