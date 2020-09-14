<?php

namespace Database\Factories;

use App\Group;
use Illuminate\Database\Eloquent\Factories\Factory;

class GroupFactory extends Factory
{
    /**
     * The name of the factory's corresponding model.
     *
     * @var string
     */
    protected $model = Group::class;

    /**
     * Define the model's default state.
     *
     * @return array
     */
    public function definition()
    {
        $codes = ['EPP', 'SD', 'RENEW', 'GREENS', 'ECR', 'GUE'];

        return [
            'code' => $this->faker->unique()->randomElement($codes),
        ];
    }
}
