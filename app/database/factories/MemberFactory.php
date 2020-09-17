<?php

namespace Database\Factories;

use App\Enums\CountryEnum;
use App\GroupMembership;
use App\Member;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Carbon;

class MemberFactory extends Factory
{
    /**
     * The name of the factory's corresponding model.
     *
     * @var string
     */
    protected $model = Member::class;

    /**
     * Define the model's default state.
     *
     * @return array
     */
    public function definition()
    {
        return [
            'web_id' => $this->faker->randomNumber(5),
            'first_name' => $this->faker->firstName(),
            'last_name' => $this->faker->lastName(),
            'date_of_birth' => $this->faker->dateTimeThisCentury(),
            'country' => CountryEnum::GB(),
        ];
    }

    public function activeAt(Carbon $date)
    {
        return $this->has(GroupMembership::factory()->activeAt($date));
    }
}
