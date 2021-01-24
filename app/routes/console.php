<?php

use App\Actions\CompileVoteStatsAction;
use App\Actions\ScrapeAndSaveMemberGroupsAction;
use App\Actions\ScrapeAndSaveMemberInfoAction;
use App\Actions\ScrapeAndSaveMembersAction;
use App\Actions\ScrapeAndSaveVoteResultsAction;
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

Artisan::command('scrape:members {term}', function (
    int $term,
    ScrapeAndSaveMembersAction $action
) {
    $term = Term::whereNumber($term)->first();
    $action->execute($term);
})->describe('Scrape and save all members (without info) for a given term.');

Artisan::command('scrape:members-info', function (ScrapeAndSaveMemberInfoAction $action) {
    $allMembers = Member::all();
    $membersCount = $allMembers->count();

    foreach ($allMembers as $index => $member) {
        $this->info('Scraping info for member: '.($index + 1)."/{$membersCount}");
        $action->execute($member);
    }
})->describe('Scrape and save info for all saved members.');

Artisan::command('scrape:members-groups {term}', function (
    int $term,
    ScrapeAndSaveMemberGroupsAction $action
) {
    $term = Term::whereNumber($term)->first();
    $allMembers = Member::all();
    $membersCount = $allMembers->count();

    foreach ($allMembers as $index => $member) {
        $this->info('Scraping groups for member '.($index + 1)."/{$membersCount}");
        $action->execute($member, $term);
    }
})->describe('Scrape and save group info for all saved members for the given term.');

Artisan::command('scrape:vote-results {term} {date}', function (
    int $term,
    string $date,
    ScrapeAndSaveVoteResultsAction $action,
    CompileVoteStatsAction $statsAction
) {
    $term = Term::whereNumber($term)->first();
    $date = Carbon::parse($date);

    $this->info("Scraping vote results for {$date}");
    $action->execute($term, $date);

    $votes = Vote::whereDate('date', '=', $date->toDateString())->get();
    $votesCount = $votes->count();

    foreach ($votes as $index => $vote) {
        $this->info('Compiling for vote '.($index + 1)."/{$votesCount}");
        $statsAction->execute($vote);
    }
})->describe('Scrape and save all votes with compiled stats for the given date and term.');
