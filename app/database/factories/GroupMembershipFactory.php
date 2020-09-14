<?php

namespace Database\Factories;

use App\Group;
use App\GroupMembership;
use App\Member;
use Illuminate\Database\Eloquent\Factories\Factory;

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
            'start_date' => $this->faker->dateTimeThisDecade(),
            'end_date' => $this->faker->dateTimeThisDecade(),
        ];
    }
}
