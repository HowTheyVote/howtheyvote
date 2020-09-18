<?php

namespace Database\Factories;

use App\Group;
use App\GroupMembership;
use App\Member;
use App\Term;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Carbon;

class GroupMembershipFactory extends Factory
{
    /**
     * The name of the factory's corresponding model.
     *
     * @var string
     */
    protected $model = GroupMembership::class;

    /**
     * Define the model's default state.
     *
     * @return array
     */
    public function definition()
    {
        return [
            'group_id' => Group::factory(),
            'member_id' => Member::factory(),
            'term_id' => Term::factory(),
            'start_date' => $this->faker->dateTimeThisDecade(),
            'end_date' => $this->faker->dateTimeThisDecade(),
        ];
    }

    public function withDate(Carbon $date)
    {
        return $this->state([
            'start_date' => $date,
            'end_date' => $date,
        ]);
    }

    public function withGroup(?Group $group)
    {
        if (! $group) {
            return $this;
        }

        return $this->state([
            'group_id' => $group->id,
        ]);
    }
}
