<?php

use App\Actions\GenerateVoteSharePicAction;
use App\Actions\ScrapeMemberGroupsAction;
use App\Actions\ScrapeMemberInfoAction;
use App\Actions\ScrapeMembersAction;
use App\Actions\ScrapeVoteResultsAction;
use App\Member;
use App\Term;
use App\Vote;
use Illuminate\Foundation\Inspiring;
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

Artisan::command('inspire', function () {
    $this->comment(Inspiring::quote());
})->describe('Display an inspiring quote');

Artisan::command('scrape:members {--term=}', function (
    int $term,
    ScrapeMembersAction $action
) {
    $term = Term::whereNumber($term)->first();
    $this->info("Scraping list of members for term {$term}");

    $action->execute($term);
})->describe('Scrape and save all members (without info) for a given term.');

Artisan::command('scrape:members-info', function (ScrapeMemberInfoAction $action) {
    $allMembers = Member::all();
    $membersCount = $allMembers->count();

    foreach ($allMembers as $index => $member) {
        $progress = ($index + 1).'/'.$membersCount;
        $this->output->write("\r<info>Scraping info for member: {$progress}</info>");

        $action->execute($member);
    }

    $this->output->writeln('');
})->describe('Scrape and save info for all saved members.');

Artisan::command('scrape:members-groups {--term=}', function (
    int $term,
    ScrapeMemberGroupsAction $action
) {
    $term = Term::whereNumber($term)->first();
    $allMembers = Member::all();
    $membersCount = $allMembers->count();

    foreach ($allMembers as $index => $member) {
        $progress = ($index + 1).'/'.$membersCount;
        $this->output->write("\r<info>Scraping groups for member {$progress}</info>");

        $action->execute($member, $term);
    }

    $this->output->writeln('');
})->describe('Scrape and save group info for all saved members for the given term.');

Artisan::command('scrape:vote-results {--term=} {--date=}', function (
    int $term,
    string $date,
    ScrapeVoteResultsAction $action
) {
    $term = Term::whereNumber($term)->first();
    $date = Carbon::parse($date);

    $this->info("Scraping vote results for {$date}");
    $action->execute($term, $date);

    $this->output->writeln('');
})->describe('Scrape and save all votes with compiled stats for the given date and term.');

Artisan::command('share-picture:vote {--vote=}', function (
    int $vote,
    GenerateVoteSharePicAction $action
) {
    $vote = Vote::find($vote);
    $action->execute($vote);
})->describe('Generates a picture showing the overall result for a given vote.');
