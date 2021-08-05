<?php

namespace App\Enums;

use Spatie\Enum\Laravel\Enum;

/**
 * @method static self AT()
 * @method static self BE()
 * @method static self BG()
 * @method static self CY()
 * @method static self CZ()
 * @method static self DE()
 * @method static self DK()
 * @method static self EE()
 * @method static self ES()
 * @method static self FI()
 * @method static self FR()
 * @method static self GB()
 * @method static self GR()
 * @method static self HR()
 * @method static self HU()
 * @method static self IE()
 * @method static self IT()
 * @method static self LT()
 * @method static self LU()
 * @method static self LV()
 * @method static self MT()
 * @method static self NL()
 * @method static self PL()
 * @method static self PT()
 * @method static self RO()
 * @method static self SE()
 * @method static self SI()
 * @method static self SK()
 */
class CountryEnum extends Enum
{
    protected static function labels(): array
    {
        return [
            'AT' => 'Austria',
            'BE' => 'Belgium',
            'BG' => 'Bulgaria',
            'CY' => 'Cyprus',
            'CZ' => 'Czech Republic',
            'DE' => 'Germany',
            'DK' => 'Denmark',
            'EE' => 'Estonia',
            'ES' => 'Spain',
            'FI' => 'Finland',
            'FR' => 'France',
            'GB' => 'United Kingdom',
            'GR' => 'Greece',
            'HR' => 'Croatia',
            'HU' => 'Hungary',
            'IE' => 'Ireland',
            'IT' => 'Italy',
            'LT' => 'Lithuania',
            'LU' => 'Luxembourg',
            'LV' => 'Latvia',
            'MT' => 'Malta',
            'NL' => 'Netherlands',
            'PL' => 'Poland',
            'PT' => 'Portugal',
            'RO' => 'Romania',
            'SE' => 'Sweden',
            'SI' => 'Slovenia',
            'SK' => 'Slovakia',
        ];
    }

    protected static function emojis(): array
    {
        return [
            'AT' => '🇦🇹',
            'BE' => '🇧🇪',
            'BG' => '🇧🇬',
            'CY' => '🇨🇾',
            'CZ' => '🇨🇿',
            'DE' => '🇩🇪',
            'DK' => '🇩🇰',
            'EE' => '🇪🇪',
            'ES' => '🇪🇸',
            'FI' => '🇫🇮',
            'FR' => '🇫🇷',
            'GB' => '🇬🇧',
            'GR' => '🇬🇷',
            'HR' => '🇭🇷',
            'HU' => '🇭🇺',
            'IE' => '🇮🇪',
            'IT' => '🇮🇹',
            'LT' => '🇱🇻',
            'LU' => '🇱🇺',
            'LV' => '🇱🇹',
            'MT' => '🇲🇹',
            'NL' => '🇳🇱',
            'PL' => '🇵🇱',
            'PT' => '🇵🇹',
            'RO' => '🇷🇴',
            'SE' => '🇸🇪',
            'SI' => '🇸🇮',
            'SK' => '🇸🇰',
        ];
    }

    public function __get(string $name)
    {
        if ($name === 'emoji') {
            return self::emojis()[$this->value];
        }

        return parent::__get($name);
    }
}
