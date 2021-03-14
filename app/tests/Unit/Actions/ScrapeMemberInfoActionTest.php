<?php

use App\Actions\ScrapeMemberInfoAction;
use App\Enums\CountryEnum;
use App\Member;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Arr;

uses(Tests\TestCase::class, RefreshDatabase::class);

it('updates member data', function () {
    $this->action = $this->app->make(ScrapeMemberInfoAction::class);
    Http::fakeJsonFromFile('*/member_info?web_id=12345', 'member_info.json');

    $member = Member::factory(['web_id' => 12345])->create();

    $this->action->execute($member);

    $attributes = $member->fresh()->getAttributes();
    $attributes = Arr::except($attributes, [
        'created_at',
        'updated_at',
        'id',
    ]);

    expect($attributes)->toEqual([
        'web_id' => 12345,
        'first_name' => 'Jane',
        'last_name' => 'Doe',
        'first_name_normalized' => 'jane',
        'last_name_normalized' => 'doe',
        'country' => CountryEnum::GB(),
        'date_of_birth' => '1975-01-01 00:00:00',
    ]);
});
